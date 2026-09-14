import ast
import io
import json
from pathlib import Path
import subprocess
import zipfile
from unittest.mock import patch
import pytest
from photo_to_storybook import cli
from photo_to_storybook.distribution import build_addon, render_engine, write_script


def test_engine_contains_assets_and_compiles():
    source = render_engine()
    tree = ast.parse(source)
    assert "__ASSET_PAYLOAD__" not in source
    assert "__VISION_SOURCE__" not in source
    assert source == render_engine()
    assert any(isinstance(node, ast.FunctionDef) and node.name == "run_cli" for node in tree.body)
    assert "/Users/" not in source
    assert "codex-clipboard" not in source


def test_addon_structure_and_overwrite_protection(tmp_path):
    output = tmp_path / "addon.zip"
    build_addon(output)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert "photo_to_storybook_blender/__init__.py" in archive.namelist()
        assert "photo_to_storybook_blender/ASSET_LICENSE.txt" in archive.namelist()
        ast.parse(archive.read("photo_to_storybook_blender/__init__.py").decode())
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        build_addon(output)
    assert output.read_bytes() == original
    build_addon(output, overwrite=True)


def test_script_existing_file_is_not_replaced(tmp_path):
    destination = tmp_path / "script.py"
    destination.write_text("user content")
    with pytest.raises(FileExistsError):
        write_script(destination)
    assert destination.read_text() == "user content"


def test_missing_input_is_reported_without_starting_blender(tmp_path, capsys):
    with patch.object(cli, "find_blender") as find:
        result = cli.main(["generate", "--image", str(tmp_path / "absent.jpg"), "--output", str(tmp_path / "new")])
    assert result == 1
    assert "Photo not found" in capsys.readouterr().err
    find.assert_not_called()
    assert not (tmp_path / "new").exists()


def test_paths_and_user_text_remain_literal_arguments(tmp_path):
    photo = tmp_path / "photo space; dollar$.png"
    photo.write_bytes(b"fixture")
    config = tmp_path / "settings.json"
    config.write_text("{}")
    lettering = 'literal $(command) `text` "quote"'
    args = cli.parser().parse_args(["generate", "--image", str(photo), "--output", str(tmp_path / "a b"),
        "--config", str(config), "--shirt-text", lettering, "--face-box", ".1", ".2", ".3", ".4", "--no-render"])
    forwarded = cli.generator_arguments(args)
    assert forwarded[forwarded.index("--shirt-text") + 1] == lettering
    assert forwarded[forwarded.index("--image") + 1] == str(photo.resolve())
    assert forwarded[-1] == "--no-render"


def test_launcher_passes_errors_through_and_keeps_script_alive(tmp_path):
    photo = tmp_path / "photo.ppm"
    photo.write_bytes(b"fixture")
    def execute(command, **kwargs):
        assert isinstance(command, list)
        assert "--factory-startup" in command
        assert command[command.index("--python-exit-code") + 1] == "1"
        generated = Path(command[command.index("--python") + 1])
        assert generated.is_file()
        ast.parse(generated.read_text())
        assert not kwargs.get("shell", False)
        return subprocess.CompletedProcess(command, 7)
    with patch.object(cli, "find_blender", return_value=Path("blender")), patch.object(cli, "check_blender", return_value="Blender 5.2.1"), patch.object(cli.subprocess, "run", side_effect=execute):
        assert cli.main(["generate", "--image", str(photo), "--output", str(tmp_path)]) == 7


@pytest.mark.parametrize("text,acceptable", [("Blender 3.6.9\n",False),("Blender 4.2.0\n",True),("Blender 5.2.1 LTS\n",True),("not blender",False)])
def test_version_compatibility(text, acceptable):
    with patch.object(cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, text, "")):
        if acceptable:
            assert cli.check_blender(Path("blender")).startswith("Blender")
        else:
            with pytest.raises(cli.BlenderError):cli.check_blender(Path("blender"))


def test_explicit_bad_blender_does_not_silently_fallback(tmp_path):
    with pytest.raises(cli.BlenderError):cli.find_blender(str(tmp_path / "missing"))


def test_config_is_json():
    data = json.loads((Path(__file__).parents[1] / "examples/config.json").read_text())
    assert data["skin_color"] is None
    assert data["overwrite"] is False

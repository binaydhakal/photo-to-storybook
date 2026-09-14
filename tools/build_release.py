"""Build add-on and standalone downloads alongside wheel/sdist from python -m build."""
from pathlib import Path
from photo_to_storybook import __version__
from photo_to_storybook.distribution import build_addon, write_script

root = Path(__file__).resolve().parents[1]
output = root / "dist"
output.mkdir(exist_ok=True)
build_addon(output / f"photo_to_storybook_blender-{__version__}.zip", overwrite=True)
write_script(output / "photo_to_storybook.py", overwrite=True)
print(f"Release downloads created in {output}")

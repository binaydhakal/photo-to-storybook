"""Create self-contained Blender scripts and installable legacy add-on archives."""
from __future__ import annotations
import base64
from importlib import resources
from pathlib import Path
import zipfile
import zlib

MODULE_NAME = "photo_to_storybook_blender"


def render_engine() -> str:
    data = resources.files("photo_to_storybook").joinpath("resources")
    template = data.joinpath("engine.py.in").read_text(encoding="utf-8")
    payload = base64.b85encode(zlib.compress(data.joinpath("makehuman.zip").read_bytes())).decode("ascii")
    vision = data.joinpath("face_detector.swift").read_text(encoding="utf-8")
    return template.replace(repr("__ASSET_PAYLOAD__"), repr(payload), 1).replace(
        repr("__VISION_SOURCE__"), repr(vision), 1
    )


def write_script(destination: Path, *, overwrite: bool = False) -> Path:
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing scripts unless replacement was requested.
    with destination.open("w" if overwrite else "x", encoding="utf-8") as output:
        output.write(render_engine())
    return destination


def build_addon(destination: Path, *, overwrite: bool = False) -> Path:
    destination = Path(destination).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = resources.files("photo_to_storybook").joinpath("resources")
    with zipfile.ZipFile(destination, "w" if overwrite else "x", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{MODULE_NAME}/__init__.py", render_engine())
        archive.writestr(f"{MODULE_NAME}/ASSET_LICENSE.txt", data.joinpath("ASSET_LICENSE.txt").read_bytes())
        archive.writestr(f"{MODULE_NAME}/LICENSE", data.joinpath("SCRIPT_LICENSE.txt").read_bytes())
        archive.writestr(f"{MODULE_NAME}/README.txt", (
            "Install this ZIP from Blender Preferences > Add-ons > Install from Disk.\n"
            "Enable Photo to Storybook 3D. Open the viewport's N sidebar > Storybook.\n"
            "Choose a photo and output directory, adjust presets, and generate.\n"
            "Approximate template-based characters; no animation rig.\n"
            "https://github.com/binaydhakal/photo-to-storybook\n"
        ))
    return destination

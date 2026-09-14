"""Small standard-library launcher; no bpy or NumPy dependency in host Python."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from . import __version__
from .distribution import build_addon, write_script


class BlenderError(RuntimeError):
    """An actionable Blender installation error."""


def _executable(value: str) -> Path | None:
    path = Path(value).expanduser()
    if path.suffix == ".app":
        path = path / "Contents" / "MacOS" / "Blender"
    if path.is_file():
        if os.name == "nt" or os.access(path, os.X_OK):
            return path.resolve()
        return None
    discovered = shutil.which(str(path))
    return Path(discovered).resolve() if discovered else None


def find_blender(explicit: str | None = None) -> Path:
    selected = explicit or os.environ.get("BLENDER_BIN")
    if selected:
        path = _executable(selected)
        if path:
            return path
        raise BlenderError(f"Blender executable not found or not executable: {selected}")
    found = shutil.which("blender")
    if found:
        return Path(found).resolve()
    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates = [Path("/Applications/Blender.app/Contents/MacOS/Blender"),
                      Path.home() / "Applications/Blender.app/Contents/MacOS/Blender"]
    elif sys.platform == "win32":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            if os.environ.get(variable):
                base = Path(os.environ[variable]) / "Blender Foundation"
                candidates.extend(sorted(base.glob("Blender*/blender.exe"), reverse=True))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise BlenderError("Install Blender 4.2 or later, then use --blender PATH or set BLENDER_BIN.")


def check_blender(executable: Path) -> str:
    try:
        result = subprocess.run([str(executable), "--version"], capture_output=True, text=True,
                                timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BlenderError(f"Could not start Blender: {exc}") from exc
    match = re.search(r"Blender\s+(\d+)\.(\d+)(?:\.(\d+))?", result.stdout)
    if result.returncode != 0 or not match:
        raise BlenderError("The selected executable did not return a valid Blender version.")
    if (int(match[1]), int(match[2])) < (4, 2):
        raise BlenderError(f"Blender 4.2 or later is required; found {match[0]}.")
    return match[0]


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(description="Local photo-guided storybook characters for Blender.")
    main.add_argument("--version", action="version", version=f"photo-to-storybook {__version__}")
    sub = main.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Find Blender and check compatibility")
    doctor.add_argument("--blender", help="Blender executable, .app directory, or command name")
    for command in ("addon", "script"):
        package = sub.add_parser(command, help=f"Export a standalone Blender {command}")
        package.add_argument("--output", required=True, type=Path)
        package.add_argument("--overwrite", action="store_true")
    generate = sub.add_parser("generate", help="Generate .blend, optional .glb, and a preview")
    generate.add_argument("--blender")
    generate.add_argument("--image", required=True, type=Path)
    generate.add_argument("--output", required=True, type=Path)
    generate.add_argument("--config", type=Path)
    generate.add_argument("--name")
    generate.add_argument("--body", choices=("neutral", "masculine", "feminine"))
    generate.add_argument("--hair", choices=("swept", "bob", "long", "bald"))
    generate.add_argument("--sunglasses", choices=("auto", "on", "off"))
    generate.add_argument("--frame", choices=("portrait", "full-body"))
    generate.add_argument("--face-box", type=float, nargs=4, metavar=("LEFT", "TOP", "WIDTH", "HEIGHT"))
    generate.add_argument("--head-scale", type=float)
    generate.add_argument("--eye-scale", type=float)
    generate.add_argument("--resolution", type=int)
    generate.add_argument("--seed", type=int)
    generate.add_argument("--shirt-text")
    for flag in ("beard", "watch", "no-render", "no-glb", "overwrite"):
        generate.add_argument(f"--{flag}", action="store_true")
    return main


def generator_arguments(args: argparse.Namespace) -> list[str]:
    image = args.image.expanduser().resolve()
    if not image.is_file():
        raise ValueError(f"Photo not found: {image}")
    output = args.output.expanduser().resolve()
    forwarded = ["--image", str(image), "--output", str(output)]
    if args.config:
        config = args.config.expanduser().resolve()
        if not config.is_file():
            raise ValueError(f"Configuration not found: {config}")
        forwarded.extend(["--config", str(config)])
    for name in ("name", "body", "hair", "sunglasses", "frame", "head_scale", "eye_scale",
                 "resolution", "seed", "shirt_text"):
        value = getattr(args, name)
        if value is not None:
            forwarded.extend(["--" + name.replace("_", "-"), str(value)])
    if args.face_box is not None:
        forwarded.append("--face-box")
        forwarded.extend(str(number) for number in args.face_box)
    for name in ("beard", "watch", "no_render", "no_glb", "overwrite"):
        if getattr(args, name):
            forwarded.append("--" + name.replace("_", "-"))
    return forwarded


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command in ("addon", "script"):
            create = build_addon if args.command == "addon" else write_script
            print(create(args.output, overwrite=args.overwrite))
            return 0
        if args.command == "doctor":
            executable = find_blender(args.blender)
            print(f"{check_blender(executable)}\nExecutable: {executable}")
            print("Ready. Face detection uses local Apple Vision on macOS when available; other systems can use manual framing.")
            return 0
        forwarded = generator_arguments(args)
        executable = find_blender(args.blender)
        print(f"Using {check_blender(executable)}", flush=True)
        with tempfile.TemporaryDirectory(prefix="photo-to-storybook-") as temporary:
            script = write_script(Path(temporary) / "generate.py")
            command = [str(executable), "--background", "--factory-startup", "--python-exit-code", "1",
                       "--python", str(script), "--", *forwarded]
            # A list of arguments avoids shell evaluation of filenames and lettering.
            return subprocess.run(command, check=False).returncode
    except (BlenderError, OSError, ValueError) as exc:
        print(f"photo-to-storybook: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130

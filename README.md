# Photo to Storybook

Turn a person’s photo into an **editable storybook/anime-inspired 3D character in Blender**. Runs locally, with no API key, subscription, or image upload.

This is an experimental **photo-guided template generator**. The photo guides colors and broad face proportions; hair, clothing, and the standing pose use adjustable presets. It does not reconstruct an exact likeness or arbitrary outfits. See [limitations](#limitations).

## Worked example

A fictional sample portrait, a runnable configuration, and a real render from the generated 3D model:

| Input | Blender output |
| --- | --- |
| ![Fictional sample input](https://raw.githubusercontent.com/binaydhakal/photo-to-storybook/main/examples/first-character/input.png) | ![Generated storybook character](https://raw.githubusercontent.com/binaydhakal/photo-to-storybook/main/examples/first-character/preview.png) |

[Follow the example](examples/first-character/README.md) · [Download the editable Blender/GLB example](https://github.com/binaydhakal/photo-to-storybook/releases/download/v1.0.1/first-character-example.zip)

## Get it

Install the Python package from [PyPI](https://pypi.org/project/photo-to-storybook/), or download the Blender add-on and standalone script from [GitHub Releases](https://github.com/binaydhakal/photo-to-storybook/releases). The repository and release downloads are public.

### Blender users — no Python setup

1. Download `photo_to_storybook_blender-1.0.1.zip` from the release.
2. In Blender, open **Edit → Preferences → Add-ons → Install from Disk**, select the ZIP, and enable **Photo to Storybook 3D**.
3. Open the 3D viewport’s **N sidebar → Storybook**.
4. Select a photo and save folder, adjust the presets, and click **Create Storybook Character**.

The generated project is created in a separate Blender process. Your current project is left open. Save your current work before opening the result.

Alternatively, download `photo_to_storybook.py` and run it from Blender’s Text Editor. The [Blender guide](docs/blender-guide.md) explains that workflow and the controls.

### Command line

Install directly from PyPI:

```sh
python -m pip install photo-to-storybook
photo-to-storybook doctor
photo-to-storybook generate --image person.jpg --output results
```

Or install from a clone:

```sh
gh repo clone binaydhakal/photo-to-storybook
cd photo-to-storybook
python -m pip install .
```

Blender must be installed separately. The launcher finds it on your PATH or in common macOS/Windows locations. If needed:

```sh
photo-to-storybook generate \
  --blender "/Applications/Blender.app/Contents/MacOS/Blender" \
  --image "/path/to/person.jpg" \
  --output "/path/to/results" \
  --hair swept --sunglasses off --head-scale 1.25
```

`BLENDER_BIN` is another way to select the executable. Use `photo-to-storybook generate --help` for all options.

## What it creates

- **`.blend`**: separate body, clothes, hair, face details and optional accessories; Eevee cel materials, outline meshes, lights, cameras, and a packed photo reference.
- **`.glb`**: optional portable export with simpler PBR materials. It does not preserve Blender-specific cel shading.
- **PNG preview**: optional render from the generated scene.
- **Recipe JSON**: reusable input settings, plus a separate diagnostic settings file.

Existing outputs receive numbered names unless `--overwrite` is explicitly supplied. The character uses a **static standing pose**, with no animation rig. Unseen surfaces and lower legs are inferred.

## Customization

Presets include neutral/masculine/feminine adult body templates, swept/bob/long/bald hair, sunglasses, a short beard, and a wristwatch. Adjust head proportions, eye size, shirt lettering, and sampled colors.

```sh
photo-to-storybook generate --image person.jpg --output results \
  --config examples/config.json --hair bob --sunglasses off
```

Colors in JSON are sRGB triples from 0–1; `null` samples the photograph. `--face-box LEFT TOP WIDTH HEIGHT` selects a face manually using normalized image coordinates with a top-left origin.

On macOS, local Apple Vision can locate a face through the system Swift toolchain. OpenCV is optional on other platforms if already available inside Blender. Otherwise, manual framing and color overrides work without either detector. Multiple-face photos use the largest detected face unless overridden.

## Other commands

```sh
photo-to-storybook doctor
photo-to-storybook addon --output storybook-addon.zip
photo-to-storybook script --output storybook.py
python -m photo_to_storybook --version
```

The Python package contains no host-runtime dependencies. Blender supplies its own Python and NumPy. All base assets are included; nothing is downloaded during generation.

## Compatibility

- Host Python **3.10+** for the optional command-line launcher.
- Blender **4.2+**. The generator was tested with Blender **5.2.1 on macOS**.
- Package tests cover Windows, macOS and Linux in CI; that does not imply the full Blender rendering workflow has been validated on each platform.
- Use **Eevee** for the native cel-shaded look.

## Limitations

A clear frontal portrait works best. Profiles, children, occlusion, complex costumes and unusual poses need substantial manual modeling. Facial identity, precise expression, hair geometry, logos, clothing patterns and pose are not automatically reconstructed. Color sampling can include photo lighting and filters. The result is a starting point for further editing.

Generated outline meshes are separate; update or remove them after substantial manual reshaping. GLB has mesh hair and portable materials, while the native file retains editable curves and Blender shaders.

## Development

```sh
python -m venv .venv
# Activate the environment using your platform's normal command.
python -m pip install -e ".[dev]"
python -m pytest -q
python -m build
python -m twine check "dist/*.whl" "dist/*.tar.gz"
python tools/build_release.py
```

The readable generator is `src/photo_to_storybook/resources/engine.py.in`; base data and the local face detector are adjacent resources. `distribution.py` assembles them into a self-contained script or Blender add-on. Host imports do not import `bpy`.

See [contributing](CONTRIBUTING.md), [release instructions](docs/releasing.md), and the [changelog](CHANGELOG.md).

## Licenses

Python/Swift application code: [MIT](LICENSE). Embedded MakeHuman base mesh, morph and rigging data: [CC0 1.0](ASSET_LICENSE.txt). The combined distribution declares `MIT AND CC0-1.0`.

Asset source: [MakeHuman Community](https://github.com/makehumancommunity/makehuman). No affiliation with Studio Ghibli or Blender Foundation. The worked example uses a fictional AI-generated portrait, with its provenance documented in the example folder.

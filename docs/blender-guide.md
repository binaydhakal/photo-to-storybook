# Photo to Storybook 3D

A standalone Blender script that creates an editable, anime/storybook-inspired 3D character from a person’s photo. The native Blender scene uses soft colors, larger eyes, a stylized head, cel shading, and drawn contours. The visual direction is inspired by hand-painted animation, including Studio Ghibli.

**This is a photo-guided character generator.** It samples a photo and adapts an anatomical template. It does not recover an accurate 3D likeness, copy an arbitrary outfit, or reconstruct the pose from pixels. A frontal, clearly visible person works best. Review the result and adjust the presets.

## Quick start — no coding required

1. Save `photo_to_storybook.py` somewhere on your computer. The script contains its own base assets.
2. Open **Blender → Scripting**. In the Text Editor, choose **Text → Open** and open the script.
3. Click **Run Script** (the triangle button, or **Alt/Option + P** while the mouse is over the Text Editor).
4. Return to the **Layout** workspace. Put the mouse over the 3D viewport, press **N**, and select the **Storybook** tab.
5. Choose a **Person photo** and a **Save folder**. Set hair, body preset, glasses, beard, and colors as needed.
6. Click **Create Storybook Character**. Generation runs in a separate Blender process, leaving your current project untouched.
7. When the panel says **Created**, open the generated `.blend` from the save folder. The panel also has an **Open Generated Blender File** button; save your current work first.

Run Script again in a new Blender session to bring the panel back. No add-on installation is required. Keep the `.py` file saved on disk; the background generator needs it.

## Outputs

- `name.blend` — editable character, native cel shaders, lighting, cameras, and packed reference image.
- `name.glb` — optional portable mesh export with simpler PBR materials.
- `name_preview.png` — optional render from the actual Blender scene.
- `name_recipe.json` — reusable settings; pass it with `--config` to reproduce or revise the character.
- `name_settings.json` — analysis and diagnostic record; this is not an input configuration file.

Existing output names are protected by default: a repeated run creates a numbered version. The command-line `--overwrite` switch explicitly replaces matching outputs.

The body, shirt, trousers, hair, beard, eyes, eyewear, watch, and shoes are separate editable parts. Hair includes editable curves. The pose is a static standing pose with hands at the trouser pockets. **There is no animation rig.**

## Photo analysis and privacy

Everything runs locally. No API key, subscription, photo upload, or runtime asset download is needed.

On macOS, the script tries Apple Vision through the system Swift toolchain to locate a face. If Swift is unavailable or analysis fails, it falls back to the framing controls. On other platforms, it can use OpenCV if that is already available in Blender’s Python; otherwise it uses the same fallback. Installing OpenCV is optional.

When several faces are detected, the largest is selected. Use **manual face box** to select another person. Hair, body preset, beard, and clothing are not automatically classified. The sunglasses estimate and color samples are heuristics and can be wrong.

The sampled photo affects the skin, hair, shirt, and trouser colors and the broad face-width adjustment. The photo’s background, logos, print designs, wrinkles, exact expression, and camera pose are not reconstructed. Skin color can reflect the photo’s lighting or color filter; use **Override sampled colors** when necessary.

## Controls

- **Hair:** swept short hair, bob, long hair, or bald.
- **Body preset:** neutral, masculine, or feminine. This is your template choice, not an inferred identity.
- **Head stylization:** 1.0–1.5; larger values make the head more pronounced.
- **Eye size:** 0.8–1.7.
- **Sunglasses:** estimate, on, or off.
- **Short beard / wristwatch:** optional.
- **Shirt lettering:** optional user-entered text; it does not read text from the photograph.
- **Color overrides:** replace the sampled palette.
- **Manual face box:** `[left, top, width, height]`, each measured as a fraction of the image. The origin is the top-left corner. For example `[0.30, 0.10, 0.40, 0.45]`.

The model uses adult template proportions. Images of children, profiles, heavy occlusion, complex costumes, and extreme poses will need substantial manual modeling. Unseen surfaces and cropped lower legs are inferred.

## Command line

macOS example:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python-exit-code 1 \
  --python "/path/to/photo_to_storybook.py" -- \
  --image "/path/to/person.jpg" \
  --output "/path/to/results" \
  --hair swept --sunglasses off --head-scale 1.25
```

Windows/Linux: replace the Blender executable path with your installed `blender` executable. Keep paths with spaces quoted.

To use the supplied configuration:

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python photo_to_storybook.py -- \
  --image person.jpg --output results --config example_config.json
```

Other options include `--body`, `--beard`, `--watch`, `--frame portrait`, `--frame full-body`, `--face-box LEFT TOP WIDTH HEIGHT`, `--eye-scale`, `--shirt-text`, `--seed`, `--resolution`, `--name`, `--no-render`, `--no-glb`, and `--overwrite`. Use `--help` after the final `--` for the full list.

JSON colors are sRGB triples in the range 0–1. Set a color to `null` to sample it from the photo. The supplied example configuration is intentionally generic; edit it for each subject.

## Rendering and editing

The `.blend` uses **Eevee** for its Shader-to-RGB cel materials. Use Eevee when rendering the native toon look. The **OUTLINES** collection contains generated contour meshes, which can be hidden for a softer look. If you substantially reshape the body after generation, you may need to update or remove those contour meshes.

The GLB contains ordinary PBR materials and omits the contour hulls. It does not preserve the exact Eevee cel shading. This is expected, since Shader-to-RGB is Blender-specific. Hair is converted to mesh in the export, while the `.blend` retains its editable curves.

## Compatibility and verification

Designed for Blender 4.2 or later; tested here with **Blender 5.2.1 on macOS**. Windows/Linux and other Blender releases have not been run in this environment. The script handles both known Eevee engine identifiers.


## Credits and licenses

Script code: MIT License, supplied as `SCRIPT_LICENSE.txt`.

Embedded anatomical base mesh, morphs, skeleton, and original skin weights: **MakeHuman Community**, CC0 1.0 Universal. The CC0 license is embedded in the script and included separately as `ASSET_LICENSE.txt`.

- MakeHuman: https://github.com/makehumancommunity/makehuman
- Asset license: https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.ASSETS.md
- Apple face-analysis API: https://developer.apple.com/documentation/vision/vndetectfacelandmarksrequest
- Blender scripting API: https://docs.blender.org/api/current/

This project is not affiliated with Studio Ghibli.

# Contributing

Open an issue with the expected behavior, observed behavior, Blender version, operating system, and minimal configuration. Use synthetic or redistributable fixtures; do not commit personal photos or generated files containing packed reference photos.

Install the development extras and run `python -m pytest -q`. Packaging changes should also pass `python -m build` and `python -m twine check "dist/*.whl" "dist/*.tar.gz"`. Inspect the wheel/sdist when changing resource handling.

Generator changes live in `src/photo_to_storybook/resources/engine.py.in`. Rebuild a standalone script with `photo-to-storybook script --output test.py`, then run it in Blender. Validate the actual `.blend`, preview, and GLB when changing modeling or export behavior. Package unit tests do not replace a render check.

Keep the core launcher usable without Blender installed. Preserve separate editable parts, existing-output protection, local processing, attribution, and honest descriptions of the generator's limitations.

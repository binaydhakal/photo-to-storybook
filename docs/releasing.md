# Releasing

## GitHub release

1. Update the project version in `pyproject.toml`, `src/photo_to_storybook/__init__.py`, the generator's `bl_info`, and any versioned download examples.
2. Update `CHANGELOG.md` and run the tests.
3. Run `python -m build`, `python -m twine check "dist/*.whl" "dist/*.tar.gz"`, then `python tools/build_release.py`.
4. Install the wheel into a clean environment; check the command line and Blender add-on.
5. Commit, create a version tag, push it, and attach the wheel, source distribution, add-on ZIP and standalone script to the matching GitHub release.

The manual **Build release downloads** workflow builds downloadable artifacts. It does not upload to PyPI or change repository visibility.

## PyPI

The package is distributed publicly as `photo-to-storybook`. Publishing is explicit; the GitHub build workflow does not upload to PyPI automatically.

Use an authorized PyPI account and a configured token or Trusted Publisher. Build a new version, validate only that version's wheel and source distribution, then upload both:

```sh
python -m twine upload --repository pypi dist/photo_to_storybook-VERSION-py3-none-any.whl dist/photo_to_storybook-VERSION.tar.gz
```

Substitute the new version. PyPI does not permit replacing an uploaded filename; publish a new version for corrections. Verify the public project page and install the published package into a clean environment before announcing a release. Attach the same version's files to GitHub Releases.

Keep credentials outside source control. The repository does not contain PyPI tokens.

References:
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- https://docs.pypi.org/trusted-publishers/

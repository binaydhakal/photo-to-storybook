# Releasing

## GitHub release

1. Update the project version in `pyproject.toml`, `src/photo_to_storybook/__init__.py`, the generator's `bl_info`, and any versioned download examples.
2. Update `CHANGELOG.md` and run the tests.
3. Run `python -m build`, `python -m twine check "dist/*.whl" "dist/*.tar.gz"`, then `python tools/build_release.py`.
4. Install the wheel into a clean environment; check the command line and Blender add-on.
5. Commit, create a version tag, push it, and attach the wheel, source distribution, add-on ZIP and standalone script to the matching GitHub release.

The manual **Build release downloads** workflow builds downloadable artifacts. It does not upload to PyPI or change repository visibility.

## Optional public package registry

The artifacts are standard Python distributions suitable for a package registry, but they are not automatically published. A private GitHub release is only accessible to authorized repository readers.

To publish on PyPI, the maintainer needs the package name, a PyPI account, and publishing authorization. Configure a scoped token or PyPI Trusted Publishing using the official instructions. Build and validate the distribution before running a registry upload. Do not put credentials in source files or commits.

After a successful public publication, update the README installation command and distribution status. Public wheels/source distributions make their included source and assets downloadable even if GitHub remains private.

References:
- https://packaging.python.org/en/latest/tutorials/packaging-projects/
- https://docs.pypi.org/trusted-publishers/

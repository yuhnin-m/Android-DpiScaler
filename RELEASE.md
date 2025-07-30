# Release Process

## 1. Pre-release checks
- `ruff check .`
- `python -m pytest`
- Manual smoke run: `python main.py`

## 2. Versioning
- Update version in `pyproject.toml`.
- Update `CHANGELOG.md` (`[Unreleased]` -> new version section).

## 3. Tagging
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 4. GitHub Release
- Create GitHub release from tag.
- Attach platform artifacts (DMG/EXE/AppImage) produced by CI or local release pipelines.
- Include checksums and release notes.

## 5. Post-release
- Open next `Unreleased` section in `CHANGELOG.md`.

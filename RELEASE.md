# Release Process

## 1. Pre-release checks
- `ruff check core gui domain services infrastructure tests packaging/scripts main.py`
- `python -m pytest -q`
- Manual smoke run: `python main.py`

## 2. Versioning
- Update `__version__` in `core/app_metadata.py`.
- Update `CHANGELOG.md` (`[Unreleased]` -> new version section).

## 3. Tagging
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 4. GitHub Release
- Pushing a `vX.Y.Z` tag triggers `.github/workflows/release.yml`.
- CI builds platform artifacts using:
  - `packaging/scripts/build_macos.sh`
  - `packaging/scripts/build_linux.sh`
  - `packaging/scripts/build_windows.ps1`
- CI publishes a GitHub Release with generated release notes and `SHA256SUMS`.
- macOS release artifacts are produced as two `.dmg` files:
  - `android_dpiscaler-macos-arm64.dmg`
  - `android_dpiscaler-macos-x64.dmg`

## 5. Post-release
- Open next `Unreleased` section in `CHANGELOG.md`.

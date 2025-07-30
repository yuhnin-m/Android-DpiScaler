# PNG2Drawable

PNG2Drawable is a desktop tool for Android developers.
It takes a source raster image and generates drawable variants for Android density buckets (`mdpi`, `hdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`).

## What it does
- Select Android project folder
- Detect available `res/` directories
- Drag-and-drop or choose an image file
- Configure density scales and output format (`PNG` / `WebP`)
- Generate `drawable-*` assets

## Quick start (source)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python main.py
```

## Requirements
- Python 3.11+
- macOS / Windows / Linux

## Project status
Current status: pre-release (alpha).
The app is functional, but active refactoring is in progress before first public release.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## Security
See [SECURITY.md](SECURITY.md).

## License
MIT, see [LICENSE](LICENSE).

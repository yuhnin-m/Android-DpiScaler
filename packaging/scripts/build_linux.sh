#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_PATH="$ROOT_DIR/packaging/pyinstaller/png2drawable.spec"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$ROOT_DIR"

APP_NAME="$("$PYTHON_BIN" - <<'PY'
from core.app_metadata import APP_NAME
print(APP_NAME)
PY
)"

rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist" "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

"$PYTHON_BIN" -m PyInstaller --noconfirm --clean "$SPEC_PATH"

if [[ ! -d "$ROOT_DIR/dist/${APP_NAME}" ]]; then
  echo "Expected dist folder not found: $ROOT_DIR/dist/${APP_NAME}" >&2
  exit 1
fi

TAR_PATH="$ARTIFACTS_DIR/${APP_NAME}-linux.tar.gz"
tar -czf "$TAR_PATH" -C "$ROOT_DIR/dist" "$APP_NAME"

echo "Linux artifact created: $TAR_PATH"

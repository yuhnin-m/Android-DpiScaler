#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SPEC_PATH="$ROOT_DIR/packaging/pyinstaller/android_dpiscaler.spec"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MACOS_ARCH_SUFFIX="${MACOS_ARCH_SUFFIX:-}"

cd "$ROOT_DIR"

APP_NAME="$("$PYTHON_BIN" - <<'PY'
from core.app_metadata import APP_NAME
print(APP_NAME)
PY
)"

APP_SLUG="$("$PYTHON_BIN" - <<'PY'
from core.app_metadata import APP_SLUG
print(APP_SLUG)
PY
)"

rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist" "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

"$PYTHON_BIN" -m PyInstaller --noconfirm --clean "$SPEC_PATH"

if [[ ! -d "$ROOT_DIR/dist/${APP_NAME}.app" ]]; then
  echo "Expected app bundle not found: $ROOT_DIR/dist/${APP_NAME}.app" >&2
  exit 1
fi

if [[ -z "$MACOS_ARCH_SUFFIX" ]]; then
  case "$(uname -m)" in
    arm64) MACOS_ARCH_SUFFIX="arm64" ;;
    x86_64) MACOS_ARCH_SUFFIX="x64" ;;
    *)
      echo "Unsupported macOS architecture: $(uname -m)" >&2
      exit 1
      ;;
  esac
fi

APP_BUNDLE="$ROOT_DIR/dist/${APP_NAME}.app"
APP_BINARY="$APP_BUNDLE/Contents/MacOS/${APP_NAME}"
BINARY_INFO="$(file "$APP_BINARY")"
echo "App binary: $BINARY_INFO"

if [[ "$MACOS_ARCH_SUFFIX" == "arm64" ]] && ! grep -q "arm64" <<<"$BINARY_INFO"; then
  echo "Expected arm64 app binary, got: $BINARY_INFO" >&2
  exit 1
fi

if [[ "$MACOS_ARCH_SUFFIX" == "x64" ]] && ! grep -q "x86_64" <<<"$BINARY_INFO"; then
  echo "Expected x86_64 app binary, got: $BINARY_INFO" >&2
  exit 1
fi

DMG_PATH="$ARTIFACTS_DIR/${APP_SLUG}-macos-${MACOS_ARCH_SUFFIX}.dmg"
hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$APP_BUNDLE" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo "macOS artifact created: $DMG_PATH"

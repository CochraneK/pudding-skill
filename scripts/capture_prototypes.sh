#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:4173}"
OUT_DIR="${2:-.qa}"
ROUTE="/stories/global-mental-health/prototypes"

mkdir -p "$OUT_DIR"

if [[ -n "${CHROME_BIN:-}" ]]; then
  CHROME="$CHROME_BIN"
else
  CHROME=""
  for candidate in google-chrome-stable google-chrome chromium chromium-browser; do
    if command -v "$candidate" >/dev/null 2>&1; then
      CHROME="$(command -v "$candidate")"
      break
    fi
  done
fi

if [[ -z "$CHROME" ]]; then
  echo "Chrome/Chromium not found. Set CHROME_BIN." >&2
  exit 1
fi

capture() {
  local alias="$1"
  local viewport="$2"
  local width="$3"
  local height="$4"
  local output="$OUT_DIR/stories-global-mental-health-prototypes-focus-${alias}-${viewport}.png"

  "$CHROME" \
    --headless=new \
    --no-sandbox \
    --disable-gpu \
    --disable-dev-shm-usage \
    --hide-scrollbars \
    --force-device-scale-factor=1 \
    --run-all-compositor-stages-before-draw \
    --virtual-time-budget=1200 \
    --window-size="${width},${height}" \
    --screenshot="$output" \
    "${BASE_URL}${ROUTE}?focus=${alias}" \
    >/dev/null 2>&1

  python - "$output" "$width" "$height" <<'PY'
import struct
import sys

path, expected_width, expected_height = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
with open(path, "rb") as handle:
    signature = handle.read(24)
if len(signature) < 24 or signature[:8] != b"\x89PNG\r\n\x1a\n":
    raise SystemExit(f"Invalid PNG screenshot: {path}")
width, height = struct.unpack(">II", signature[16:24])
if (width, height) != (expected_width, expected_height):
    raise SystemExit(f"Unexpected screenshot size for {path}: {width}x{height}, expected {expected_width}x{expected_height}")
PY

  echo "CAPTURE ${alias} ${viewport} → ${output}"
}

for alias in A B C; do
  capture "$alias" desktop 1440 900
  capture "$alias" mobile 390 844
done

#!/usr/bin/env bash
# Merge Origo full-ISO parts into a single .iso (Linux/macOS).
# Place this file next to origo-v0.1-full-amd64.part00, .part01, ...
set -euo pipefail
cd "$(dirname "$0")"

OUT="origo-v0.1-full-amd64.iso"
shopt -s nullglob
parts=(origo-v0.1-full-amd64.part*)
if [ "${#parts[@]}" -eq 0 ]; then
  echo "No parts found. Put origo-v0.1-full-amd64.part00 / .part01 next to this script." >&2
  exit 1
fi
cat "${parts[@]}" > "$OUT"
echo "Done: $OUT"

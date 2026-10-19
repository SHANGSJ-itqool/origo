#!/usr/bin/env bash
# Build the Origo ISO inside WSL on the Linux-native filesystem.
#
# Why: live-build uses chroot/device nodes and cannot build on /mnt/c or /mnt/h
# (Windows drvfs). We sync the repo into ~/origo inside WSL, build there, then
# copy the ISO back to the Windows drive (H:).
#
# Run inside WSL (wsl -d Origo) as root:
#   bash /mnt/h/origo/origo/scripts/build-in-wsl.sh
#
# Pass build options via env, e.g.
#   WITH_OLLAMA=1 bash /mnt/h/origo/origo/scripts/build-in-wsl.sh
set -euo pipefail

SRC="/mnt/h/origo/origo"
WORK="/root/origo"
OUT="${SRC}/dist"

echo "==> Syncing repo into WSL native fs: ${WORK}"
mkdir -p "${WORK}"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude '.git' --exclude '.venv' --exclude '__pycache__' "${SRC}/" "${WORK}/"
else
  cp -a "${SRC}/." "${WORK}/"
fi

echo "==> Building ISO in ${WORK}/iso"
mkdir -p "${OUT}"
cd "${WORK}/iso"
bash ./build.sh

echo "==> Copying ISO to ${OUT}"
cp "${WORK}"/iso/build/*.iso "${OUT}/" 2>/dev/null || true
ls -lh "${OUT}"
echo "Done. ISO is on H: at H:\\origo\\dist"

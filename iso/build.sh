#!/usr/bin/env bash
# Origo ISO build script (run on Debian/Ubuntu or in the provided Docker image).
#
# Usage:
#   sudo ./build.sh
#
# Options (environment variables):
#   DIST=trixie              Debian suite (default: trixie)
#   MIRROR=http://...        Debian mirror (default: USTC for China)
#   WITH_OLLAMA=1            install Ollama local model runtime (default 1)
#   WITH_MODEL=1             pre-pull a small model (default 1; needs network)
#   ORIGO_MODEL_TAG=qwen3:1.7b
#   OLLAMA_MIRROR=URL        custom install script URL
#
# Output: build/*.iso
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DIST="${DIST:-trixie}"
MIRROR="${MIRROR:-http://mirrors.ustc.edu.cn/debian}"
SECURITY_MIRROR="${SECURITY_MIRROR:-http://mirrors.ustc.edu.cn/debian-security}"
# Origo ships a local "brain" by default; set WITH_OLLAMA=0 for a slim image.
WITH_OLLAMA="${WITH_OLLAMA:-1}"
WITH_MODEL="${WITH_MODEL:-1}"
ORIGO_MODEL_TAG="${ORIGO_MODEL_TAG:-qwen3:1.7b}"
OLLAMA_MIRROR="${OLLAMA_MIRROR:-}"
export WITH_OLLAMA WITH_MODEL ORIGO_MODEL_TAG OLLAMA_MIRROR

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo ./build.sh)." >&2
  exit 1
fi

if [[ "${WITH_OLLAMA}" = "0" ]]; then
  echo "!! WARNING: building WITHOUT a local model runtime. The agent will have" >&2
  echo "!! no 'brain' until you install Ollama or configure a cloud backend; it" >&2
  echo "!! will show setup guidance instead of crashing." >&2
fi

echo "==> Installing live-build and required host tools..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  live-build live-config debootstrap cpio xorriso isolinux squashfs-tools \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools curl ca-certificates

WORK="${SCRIPT_DIR}/build"
echo "==> Preparing work directory: ${WORK}"
rm -rf "${WORK}"
mkdir -p "${WORK}"
cd "${WORK}"

echo "==> Running lb config (dist=${DIST}, mirror=${MIRROR})..."
lb config \
  --distribution "${DIST}" \
  --architectures amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --apt-recommends false \
  --debian-installer live \
  --debian-installer-gui true \
  --mirror-bootstrap "${MIRROR}" \
  --mirror-chroot "${MIRROR}" \
  --mirror-binary "${MIRROR}" \
  --mirror-chroot-security "${SECURITY_MIRROR}" \
  --mirror-binary-security "${SECURITY_MIRROR}" \
  --iso-volume "Origo Live" \
  --iso-publisher "Origo/元启 OS" \
  --checksums sha256

echo "==> Overlaying Origo config..."
cp -r "${SCRIPT_DIR}/debian/package-lists/." config/package-lists/
cp -r "${SCRIPT_DIR}/debian/hooks/." config/hooks/
chmod +x config/hooks/normal/*.hook.chroot || true
cp -r "${SCRIPT_DIR}/debian/includes.chroot/." config/includes.chroot/

# Lay the agent code into the image at /opt/origo/agent.
mkdir -p config/includes.chroot/opt/origo
cp -r "${REPO_ROOT}/agent" config/includes.chroot/opt/origo/agent
# Strip any local virtualenv/caches.
rm -rf config/includes.chroot/opt/origo/agent/.venv \
       config/includes.chroot/opt/origo/agent/**/__pycache__ || true
find config/includes.chroot/opt/origo -name '__pycache__' -type d -prune -exec rm -rf {} + || true

echo "==> Building image (this can take a while)..."
lb build

echo "==> Build artifacts:"
ls -lh "${WORK}"/*.iso 2>/dev/null || true
echo "Done. Flash the ISO or test it in a VM."

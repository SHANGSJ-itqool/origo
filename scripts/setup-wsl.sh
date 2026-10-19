#!/usr/bin/env bash
# Prepare an Ubuntu/WSL2 environment for building Origo.
# Run inside WSL: bash scripts/setup-wsl.sh
set -euo pipefail

MIRROR="${MIRROR:-mirrors.ustc.edu.cn}"
RELEASE_CODENAME="$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")"

echo "==> Configuring apt to use ${MIRROR} (${RELEASE_CODENAME})..."
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak 2>/dev/null || true
sudo tee /etc/apt/sources.list >/dev/null <<EOF
deb https://${MIRROR}/ubuntu ${RELEASE_CODENAME} main restricted universe multiverse
deb https://${MIRROR}/ubuntu ${RELEASE_CODENAME}-updates main restricted universe multiverse
deb https://${MIRROR}/ubuntu ${RELEASE_CODENAME}-backports main restricted universe multiverse
deb https://${MIRROR}/ubuntu ${RELEASE_CODENAME}-security main restricted universe multiverse
EOF

echo "==> Installing build tools..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  live-build live-config debootstrap cpio xorriso isolinux squashfs-tools \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools \
  curl ca-certificates git bash-completion

echo "==> (Optional) Install Ollama in this WSL for local development..."
read -r -p "Install Ollama now? [y/N] " ans
if [[ "${ans,,}" == "y" ]]; then
  curl -fsSL https://ollama.com/install.sh | sh
  echo "Then run: ollama pull qwen3:1.7b"
fi

echo "WSL environment ready. Next: cd <repo>/iso && sudo ./build.sh"

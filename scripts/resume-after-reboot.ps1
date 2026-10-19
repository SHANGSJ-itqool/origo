# Origo — resume after reboot.
# Run this in PowerShell after the machine has rebooted (WSL2/Virtual Machine Platform needs the reboot).
# It imports the downloaded Ubuntu rootfs and verifies the build environment.

$ErrorActionPreference = "Stop"

$rootfs = "H:\origo\wsl\ubuntu-noble-rootfs.tar.gz"
$installDir = "H:\origo\wsl\Origo"

if (-not (Test-Path $rootfs)) {
    throw "rootfs not found: $rootfs"
}
New-Item -ItemType Directory -Force -Path $installDir | Out-Null

Write-Output "==> Importing Ubuntu rootfs as WSL distro 'Origo'..."
wsl --import Origo $installDir $rootfs

Write-Output "==> Installed distros:"
wsl -l -v

Write-Output "==> Verifying Linux environment..."
wsl -d Origo -u root -- bash -c "cat /etc/os-release | head -2; uname -r"

Write-Output "==> Configuring apt mirror and installing build tools..."
$repo = "H:\origo\origo"
# Convert the Windows repo path to a WSL path for invocation.
$wslRepo = "/mnt/h/origo/origo"
wsl -d Origo -u root -- bash -lc "bash ${wslRepo}/scripts/setup-wsl.sh"

Write-Output "Environment ready. Next: build the ISO (see iso/README.md)."

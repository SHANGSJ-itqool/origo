# Installing Origo

## 1. Get the ISO
Download the latest `origo-*.iso` from the project's Releases page. Verify the SHA-256 checksum when available.

## 2. Create bootable media
- **Linux**: `sudo dd if=origo-*.iso of=/dev/sdX bs=4M status=progress && sync`
- **Windows**: use Rufus (DD mode) or balenaEtcher.
- **macOS**: use balenaEtcher.

## 3. Boot
Insert the USB and boot from it (use the boot menu, typically F12/F11/Esc depending on the machine). Disable Secure Boot if it blocks the image, or use the signed option when available.

## 4. Try (Live)
Choose **Live** to run Origo without changing your disk. The Origo agent opens automatically.

## 5. Install
Choose **Install** (or launch Calamares from the live desktop):
1. Select language, location, keyboard.
2. Choose the target disk (partitioning is your responsibility; use a dedicated machine or free space).
3. Create your user and password.
4. Let the installer finish, then reboot and remove the USB.

## 6. First boot
The Origo agent opens on login. If no local model is bundled, follow the first-run prompts to install a model (or use your own OpenAI-compatible endpoint). The classic desktop is available for direct control.

## Requirements (v0.1)
- 64-bit x86 PC (ARM64 image follows later)
- 2 GB RAM minimum (4 GB recommended for the local model)
- ~20 GB free disk space
- Internet for first-run setup; fully offline images available via build options

## Troubleshooting
- **Black screen at boot**: try the boot menu's safe/fallback graphics option; check firmware support.
- **No Wi-Fi**: some firmware is included; report the chipset (`lspci`/`lsusb`) in an issue.
- **Agent cannot reach a model**: confirm Ollama is running (`systemctl status ollama`) or set your endpoint via environment variables.
- **Reinstall/repair**: re-run the live image and installer.

Origo is a prototype with no warranty; back up important data before testing.

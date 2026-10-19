# Building the Origo ISO

The ISO is built with **Debian live-build** (v0.1 targets Debian *trixie*, amd64). It can run inside a Debian/Ubuntu system, WSL2, or the provided Docker image.

## Option A — native (Debian/Ubuntu)

```bash
cd iso
sudo ./build.sh
```

## Option B — Docker (recommended on Windows / for reproducibility)

```bash
docker build -t origo-builder -f iso/docker/Dockerfile .
docker run --rm -it --privileged \
  -v "$PWD/iso/build:/origo/iso/build" origo-builder
```

## Option C — WSL2 (Windows)

After rebooting and importing the Ubuntu environment (see project root `scripts/setup-wsl.sh`):

```bash
bash scripts/setup-wsl.sh   # configures mirror + installs live-build
cd /mnt/c/Users/shang/DoubaoWork/chats/2026-10-18/new-chat/origo/iso
sudo ./build.sh
```

## Build options

| Variable | Default | Meaning |
| --- | --- | --- |
| `DIST` | `trixie` | Debian suite |
| `MIRROR` | USTC | Debian mirror (China-friendly) |
| `WITH_OLLAMA` | `0` | install Ollama runtime in the image |
| `WITH_MODEL` | `0` | pre-pull a small model (network-heavy) |
| `ORIGO_MODEL_TAG` | `qwen3:0.6b` | model to pre-pull |
| `OLLAMA_MIRROR` | empty | custom Ollama install script URL |

Examples:

```bash
sudo WITH_OLLAMA=1 ./build.sh                       # include Ollama
sudo WITH_OLLAMA=1 WITH_MODEL=1 ./build.sh          # offline-ready image (larger)
```

## Notes

- v0.1 defaults to **no bundled model** to keep the image small and build robust; the agent guides first-run setup. Pre-pull with `WITH_MODEL=1` for fully offline use.
- Output ISO appears in `iso/build/`.
- Test in a VM (e.g. VirtualBox/QEMU) before flashing; UEFI and BIOS boot are both configured.

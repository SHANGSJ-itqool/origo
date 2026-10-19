# Origo ISO build environment (containerized).
# Build:
#   docker build -t origo-builder -f iso/docker/Dockerfile .
#   docker run --rm -it --privileged -v "$PWD/iso/build:/origo/iso/build" origo-builder
FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      live-build live-config debootstrap cpio xorriso isolinux squashfs-tools \
      grub-pc-bin grub-efi-amd64-bin mtools dosfstools curl ca-certificates \
      bash coreutils findutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /origo
COPY . /origo

# Note: live-build needs a privileged container for loop mounts.
CMD ["bash", "iso/build.sh"]

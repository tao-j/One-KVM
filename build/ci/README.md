# ARM64 HID candidate

This fork's candidate branch starts from upstream v261001
(`b5d13ee16e099df4082e1da96a37db0888c57bb7`). The application change shares mouse
state between OTG and CH9329 and fixes buttons/wheel for an absolute-only OTG
profile. Host deployment scripts, machine configuration, credentials, and unrelated
capture/auth/configfs patches are not part of this repository change.

Open a PR against this fork's `stock-v261001` branch to run:

1. The media-free HID component tests on native ARM64 Linux.
2. An ARM64 application cross-build on a hosted x64 runner using the upstream
   Debian 12 FFmpeg/RKMPP/RGA SDK recipe with pinned Rust/MPP/RGA/x264 inputs.
3. A derived image using the exact stock runtime digest, replacing only
   `/usr/bin/one-kvm`. The compiled frontend is copied from an isolated, no-device
   instance of that stock image; no npm/frontend build is needed.

The SDK's first build still compiles media dependencies. Docker layer and Cargo
caches allow later HID changes to reuse that work. The original all-platform
Build workflow skips this dedicated base branch; upstream PR behavior is otherwise
unchanged. Docker Hub/other registry publisher workflows are not invoked.

The candidate workflow uploads a compressed Docker archive, binary/image hashes,
source revision, stock frontend file hashes, SDK image ID and package inventory.
Load the downloaded archive with `zstd -dc one-kvm-hid-arm64.tar.zst | docker load`.
It does not publish a registry package or deploy to any machine automatically.

The new executable is a source build, not a binary edit of the stock executable.
Stock image metadata did not establish the exact source revision of its embedded
libraries. The pinned upstream SDK recipe establishes this candidate's provenance;
it does not prove byte identity with the stock media stack. Compiler/package
receipts and source pins are retained, but Debian apt repositories are not frozen
snapshots, so this is not a claim of bit-for-bit reproducibility.

CI verifies compilation, component behavior and ARM64 executable loading under
emulation. Hosted runners have no Rockchip hardware: actual hardware codec
initialization, the existing NV20 input preload, scoped HID device access, guest
click/wheel/drag/release behavior and peer isolation must pass separately before
production rollout. A build pass alone is not hardware acceptance.

For upstream submission, port the source/test commits to current upstream main
and keep these fork-specific candidate packaging/workflow changes separate.

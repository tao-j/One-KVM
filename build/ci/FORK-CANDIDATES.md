# Pre-merge images in this fork

The `Fork candidate images` workflow builds this fork's `ci/candidate-images`
branch on push (or manual dispatch). Update that branch by merging the source
revision to qualify, retaining the fork-only workflow. It is intentionally
separate from the upstream HID PR.

It uses upstream's normal Vue build, Debian 12 SDK Dockerfiles and minimal
runtime packaging. AMD64 and ARM64 compile in independent jobs; ARM64 enables
RKMPP, AMD64 retains upstream VAAPI support. SDK layers and Cargo outputs are
cached. First builds can be substantially slower than subsequent source builds.
AMD64 runs the integrated HID tests; both runtime images execute `--version`
without devices or privileges (ARM64 uses QEMU on the build runner).

The built-in GITHUB_TOKEN has packages:write only in publication jobs. No Docker
Hub credentials, production SSH keys, deployments or latest-tag updates occur.
The workflow runs only in tao-j/One-KVM. It does not publish arbitrary external
pull-request code with write credentials.

After both architecture jobs succeed:

```
docker pull ghcr.io/tao-j/one-kvm:candidate-<full-source-sha>
```

Docker selects linux/amd64 or linux/arm64. Architecture-specific tags append
`-amd64` or `-arm64`. Retain the manifest digest when promoting to production;
tags themselves are not immutable registry objects. Archives, source revision,
SDK package list, image inspection and SHA-256 receipts are downloadable from
Actions for 14 days. GHCR package visibility follows GitHub's package settings;
private pulls require package-read authentication.

This establishes build and startup compatibility, not hardware qualification.
Before deploying, qualify codec/capture and HID paths on the target host using
restricted device views and active host-input protection. Existing production
images are not changed by a successful build.

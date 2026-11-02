#!/usr/bin/env bash
set -euo pipefail
: "${ARCH:?}" "${TARGET:?}" "${REVISION:?}"
[[ "$REVISION" =~ ^[0-9a-f]{40}$ ]]
case "$ARCH:$TARGET" in
  amd64:x86_64-unknown-linux-gnu) features=() ;;
  arm64:aarch64-unknown-linux-gnu) features=(--features rkmpp) ;;
  *) exit 2 ;;
esac
mkdir -p .ci-cargo-registry .ci-cargo-git artifacts
sdk=(docker run --rm -e CARGO_BUILD_JOBS=3 -v "$PWD:/work" -w /work
  -v "$PWD/.ci-cargo-registry:/root/.cargo/registry"
  -v "$PWD/.ci-cargo-git:/root/.cargo/git" one-kvm-sdk:local)
"${sdk[@]}" cargo build --locked --release --target "$TARGET" --bin one-kvm "${features[@]}"
if [[ "$ARCH" == amd64 ]]; then
  "${sdk[@]}" cargo test --locked --release --target "$TARGET" --bin one-kvm hid::
fi
sudo chown -R "$(id -u):$(id -g)" target .ci-cargo-registry .ci-cargo-git
bash build/package-docker.sh --platform "linux/$ARCH" --image-name one-kvm-candidate --tag "$ARCH" --load
# Add provenance without changing the upstream runtime content.
mkdir -p "$RUNNER_TEMP/candidate-labels"
cat > "$RUNNER_TEMP/candidate-labels/Dockerfile" <<LABELS
FROM one-kvm-candidate:$ARCH
LABEL org.opencontainers.image.source="https://github.com/tao-j/One-KVM"
LABEL org.opencontainers.image.revision="$REVISION"
LABEL org.opencontainers.image.title="One-KVM pre-merge candidate"
LABELS
docker build --platform "linux/$ARCH" -t "one-kvm-candidate:$ARCH" "$RUNNER_TEMP/candidate-labels"
docker run --rm --platform "linux/$ARCH" --read-only --cap-drop ALL \
  --security-opt no-new-privileges --entrypoint /usr/bin/one-kvm "one-kvm-candidate:$ARCH" --version
sha256sum "target/$TARGET/release/one-kvm" > artifacts/binary.sha256
printf '%s\n' "$REVISION" > artifacts/source-revision.txt
docker image inspect "one-kvm-candidate:$ARCH" > artifacts/image.json
docker image inspect one-kvm-sdk:local --format '{{.Id}}' > artifacts/sdk-image-id.txt
docker run --rm one-kvm-sdk:local dpkg-query -W > artifacts/sdk-packages.txt
docker save "one-kvm-candidate:$ARCH" | zstd -T0 -3 -o "artifacts/one-kvm-$ARCH.tar.zst"
sha256sum "artifacts/one-kvm-$ARCH.tar.zst" > artifacts/image.sha256

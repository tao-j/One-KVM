# HID component regression tests

Place this directory at `test/hid-component` in the One-KVM source tree. It
directly includes the real application HID modules through repository-relative
`#[path]` attributes; it does not copy or reimplement their mouse logic.

Run from the repository root on Linux or macOS:

```sh
cargo test --locked --manifest-path test/hid-component/Cargo.toml
```

No media SDK, frontend build, USB gadget, UART, elevated permission or device
access is needed. OTG reports are written to ordinary temporary files. CH9329
tests inspect the actual worker-command queue. Serialport's optional libudev
discovery feature is disabled in this harness because no port is opened.

The crate pins direct dependency versions from the application lockfile and
has its own committed lockfile. Its empty `[workspace]` keeps the media dependency
graph and application build script out of component testing.

Included actual modules: `mouse_state`, `otg`, `otg_device`, `ch9329`,
`ch9329_proto`, `macos_drag`, `keyboard`, `types` and `backend`. The small
`src/lib.rs` defines fixture application error/config/event types and inert
gadget discovery. These fixtures are not hardware implementations.

The new shared-state and adapter regression tests live inside the production
source files under `#[cfg(test)]`. Thus the normal application test build also
compiles and executes the same tests with the real surrounding application types:

```sh
# Run in the application's supported Linux build/link environment.
cargo test --locked --bin one-kvm hid::mouse_state::tests
cargo test --locked --bin one-kvm hid::otg::tests
cargo test --locked --bin one-kvm hid::ch9329::tests
cargo test --locked --bin one-kvm hid::macos_drag::tests
```

The component suite verifies common state, exact report bytes, serial scaling,
drag, release/reset, missing endpoints, relative/dual/hybrid/macOS behavior and
concurrent event/output ordering. It does not establish full application linking,
ARM64 ABI compatibility, physical USB/serial behavior or guest acceptance.

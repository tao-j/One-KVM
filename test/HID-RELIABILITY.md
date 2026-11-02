# HID click reliability checks

The single-controller input path preserves transport/admission/FIFO order and
uses explicit failure recovery rather than silently dropping button edges.
WebRTC is ordered and reliable. Its awaited callback feeds the existing bounded
controller queue; movement has no separate priority slot. Overflow, cancelled
admission, or delivery error invalidates the queued batch. Input stays blocked
until a successful neutral release for the current failure generation.

OTG mouse writes have a 100 ms total deadline, and mouse state commits only on
successful kernel writes. Failed release is retried during recovery. Idle
secondary connections do not reset active input; disconnect releases only the
keys/buttons admitted by that connection. Conflicting simultaneous controllers
holding the same key/button are outside this ownership model.

Run the media-free source tests:

```sh
cargo test --locked --manifest-path test/hid-component/Cargo.toml
cargo test --locked --manifest-path test/hid-queue/Cargo.toml
cargo test --locked --manifest-path test/hid-session/Cargo.toml
```

These execute the actual adapter, queue, session and protocol modules, with
fixtures for the surrounding application. They cover timeouts, release recovery,
queue saturation, admission cancellation, reset races and disconnect cleanup.
The application build in CI separately type-checks the controller and transport
integration against the pinned media SDK.

CI copies the pinned stock frontend, then runs the hash-locked
`build/ci/patch-stock-hid-transport.py` transformation. It changes only qualified
HID transport functions and versions the complete asset graph to prevent mixed
caches. Original and transformed hashes are retained. No npm/frontend rebuild
is required. Tests execute the transformed compiled functions with mocked
browser dependencies and check exact mouse packets, reliable options, errors,
no mid-gesture fallback, old-channel isolation and retained MJPEG behavior.

Admission and kernel-write success are not guest delivery acknowledgements.
Failure recovery may cancel an incomplete gesture; it does not replay stale
clicks. Hardware, actual guest behavior, and peer isolation still require runtime
qualification. A fresh root URL/hard reload is required for clients caching old
HTML. While a backend is absent, recovery remains blocked and retries at a
bounded rate until it returns; physical disconnection cannot guarantee release.

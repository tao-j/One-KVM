# HID delivery reliability

Absolute-only OTG profiles use the absolute endpoint for motion, button edges and
wheel events. OTG and CH9329 share canonical mouse state, while descriptor,
serial framing, scaling and adapter policy remain adapter-owned.

WebRTC uses ordered reliable delivery and awaits each ingress callback. A single
bounded FIFO admits real motion and button/key edges. Saturation, cancelled
admission and write failure invalidate stale work and block new input until a
neutral release succeeds. Reset generations prevent stale completion from
clearing newer failures. Mouse writes have a bounded 100 ms deadline and commit
state only after success. Disconnect cleanup releases that connection's admitted
held inputs; an idle connection does not reset a peer.

This port preserves upstream's confirmed input APIs, bounded relative-delta
splitting, mouse jiggler and keyboard shortcuts. Synthetic jiggler motion remains
serialized in the worker and observes the recovery barrier. The removed stream
WebSocket implementation is not restored. Frontend changes are made in Vue/TS
source; no stock compiled-asset transformation or deployment image build is added.

## Tests

```sh
cargo test --locked --manifest-path test/hid-component/Cargo.toml
cargo test --locked --manifest-path test/hid-queue/Cargo.toml
cargo test --locked --manifest-path test/hid-session/Cargo.toml
cd web && npm ci && npm run build
```

These harnesses compile actual adapter, state, protocol, queue and session modules
with fixtures for their application surroundings. They do not compile the full
controller/transport integration. The normal application build validates that
integration; its tests also cover confirmed delivery, relative splitting and
jiggler behavior.

76 focused Rust tests and the frontend build passed locally for this port.
An earlier pinned-release implementation passed actual-app regular-file USB
report fixtures, 40 rapid right-click sequences over real WebRTC, and three
native right-click opens plus three left-click dismissals on a Windows desktop.
Those runtime results are supporting evidence, not runtime qualification of this
new main-branch integration.

Queue admission and kernel writes are not guest acknowledgements. Conflicting
simultaneous controllers holding the same key/button are unsupported. Physical
disconnection cannot guarantee release. Long endurance and comprehensive guest
scroll/drag/modifier behavior remain unqualified.

#[path="../../../src/hid/keyboard.rs"] pub mod keyboard;
#[path="../../../src/hid/types.rs"] pub mod types;
#[path="../../../src/hid/datachannel.rs"] pub mod datachannel;
#[path="../../../src/hid/input_session.rs"] pub mod input_session;
pub use keyboard::CanonicalKey;
pub use types::{KeyEventType, KeyboardEvent, KeyboardModifiers, ConsumerEvent, MouseEvent, MouseEventType, MouseButton};
// Only controller surroundings are fixture code; tests inject their InputSink.
pub struct HidController;
impl HidController {
    pub async fn send_keyboard(&self, _: KeyboardEvent) -> crate::error::Result<()> { Ok(()) }
    pub async fn send_mouse(&self, _: MouseEvent) -> crate::error::Result<()> { Ok(()) }
    pub async fn send_consumer(&self, _: ConsumerEvent) -> crate::error::Result<()> { Ok(()) }
}

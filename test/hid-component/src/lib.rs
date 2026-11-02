//! Compile actual HID sources without the media/application dependency graph.
//! Only surrounding configuration/errors/events and gadget discovery are fixtures.
#![allow(dead_code)]
pub mod hid;
pub mod error {
    #[derive(Debug)]
    pub enum AppError {
        Internal(String),
        Config(String),
        BadRequest(String),
        HidError {
            backend: String,
            reason: String,
            error_code: String,
        },
    }
    impl std::fmt::Display for AppError {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            write!(f, "{self:?}")
        }
    }
    impl std::error::Error for AppError {}
    pub type Result<T> = std::result::Result<T, AppError>;
}
pub mod config {
    pub enum HidBackend { Otg, Ch9329, Ch9329Otg, Bluetooth, None }
    pub struct HidConfig {
        pub backend: HidBackend,
        pub mouse_macos_drag: bool,
        pub ch9329_port: String,
        pub ch9329_baudrate: u32,
        pub ch9329_hybrid_mouse: bool,
        pub bluetooth: BluetoothHidConfig,
    }

    use serde::{Deserialize, Serialize};
    #[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
    pub struct BluetoothHidConfig;
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub struct Ch9329DescriptorConfig {
        pub vendor_id: u16,
        pub product_id: u16,
        pub manufacturer: String,
        pub product: String,
        pub serial_number: Option<String>,
    }
    impl Default for Ch9329DescriptorConfig {
        fn default() -> Self {
            Self {
                vendor_id: 0x1a86,
                product_id: 0xe129,
                manufacturer: "WCH.CN".into(),
                product: "CH9329".into(),
                serial_number: None,
            }
        }
    }
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub struct Ch9329DescriptorState {
        pub descriptor: Ch9329DescriptorConfig,
        pub manufacturer_enabled: bool,
        pub product_enabled: bool,
        pub serial_enabled: bool,
        pub config_mode_available: bool,
    }
}
pub mod events {
    #[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
    pub struct LedState {
        pub num_lock: bool,
        pub caps_lock: bool,
        pub scroll_lock: bool,
        pub compose: bool,
        pub kana: bool,
    }
}
pub mod otg {
    use std::path::PathBuf;
    #[derive(Debug, Clone, Default)]
    pub struct HidDevicePaths {
        pub keyboard: Option<PathBuf>,
        pub mouse_relative: Option<PathBuf>,
        pub mouse_absolute: Option<PathBuf>,
        pub consumer: Option<PathBuf>,
        pub udc: Option<String>,
        pub keyboard_leds_enabled: bool,
    }
    pub async fn wait_for_hid_devices(paths: &[PathBuf], _: u64) -> bool {
        paths.iter().all(|path| path.is_file())
    }
    pub mod configfs {
        pub fn find_udc() -> Option<String> {
            None
        }
    }
}

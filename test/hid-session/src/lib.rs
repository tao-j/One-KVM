#![allow(dead_code)]
pub mod hid;
pub mod error {
    #[derive(Debug)] pub enum AppError {BadRequest(String)}
    pub type Result<T> = std::result::Result<T, AppError>;
}

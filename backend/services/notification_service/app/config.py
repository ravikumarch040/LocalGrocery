"""Configuration settings for Notification Service"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    
    # Firebase (FCM)
    FIREBASE_PROJECT_ID: str = "localgrocery-dev"
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FCM_ENABLED: bool = False
    
    # MSG91 (SMS)
    MSG91_AUTH_KEY: Optional[str] = None
    MSG91_ROUTE: str = "4"  # Promotional/Transactional
    MSG91_ENABLED: bool = False
    
    # OTP
    OTP_LENGTH: int = 6
    OTP_VALIDITY_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    OTP_RESEND_WAIT_SECONDS: int = 60
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    # Settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    
    # Redis
    REDIS_URL: str = "redis://:dev_password_change_in_prod@localhost:6379/0"
    
    # Firebase Cloud Messaging (FCM)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None  # Path to service account JSON
    FCM_ENABLED: bool = False  # Enable in production with credentials
    
    # MSG91 SMS Provider
    MSG91_AUTH_KEY: Optional[str] = None
    MSG91_SENDER_ID: str = "LOCGRO"  # 6-character sender ID
    MSG91_ROUTE: str = "4"  # 4 = Transactional route
    MSG91_COUNTRY: str = "91"  # India country code
    MSG91_ENABLED: bool = False  # Enable in production
    
    # Notification settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY_SECONDS: int = 5
    NOTIFICATION_BATCH_SIZE: int = 100
    
    # OTP settings
    OTP_EXPIRY_MINUTES: int = 10
    OTP_LENGTH: int = 6
    
    # Template paths
    TEMPLATE_DIR: str = "app/templates"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"
    DELIVERY_SERVICE_URL: str = "http://localhost:8005"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

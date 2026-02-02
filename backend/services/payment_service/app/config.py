"""Payment Service configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery_test"
    
    # Redis
    REDIS_URL: str = "redis://:dev_password_change_in_prod@localhost:6379/0"
    
    # Service info
    SERVICE_NAME: str = "payment-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Payment Gateways
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = None
    
    CASHFREE_APP_ID: Optional[str] = None
    CASHFREE_SECRET_KEY: Optional[str] = None
    CASHFREE_WEBHOOK_SECRET: Optional[str] = None
    
    # Gateway settings
    PAYMENT_GATEWAY_TIMEOUT: int = 30  # seconds
    RAZORPAY_ENVIRONMENT: str = "sandbox"  # sandbox or production
    CASHFREE_ENVIRONMENT: str = "TEST"  # TEST or PROD
    
    # Order Service
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    # Currency
    DEFAULT_CURRENCY: str = "INR"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

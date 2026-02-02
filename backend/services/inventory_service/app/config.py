from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Inventory Service Configuration"""
    
    # Service
    SERVICE_NAME: str = "inventory_service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    
    # Redis
    REDIS_URL: str = "redis://:dev_password_change_in_prod@localhost:6379/0"
    REDIS_CACHE_TTL_MINUTES: int = 60  # Cache invalidation period
    
    # Inventory Configuration
    RESERVATION_VALIDITY_MINUTES: int = 15  # Cart holds stock for 15 mins
    LOW_STOCK_THRESHOLD_PERCENT: float = 0.20  # Alert if stock < 20% of reorder_level
    STOCK_CLEANUP_INTERVAL_MINUTES: int = 5  # Cleanup expired reservations
    
    # Service URLs
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    CATALOG_SERVICE_URL: str = "http://localhost:8002"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

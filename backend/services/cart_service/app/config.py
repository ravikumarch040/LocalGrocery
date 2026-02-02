from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Cart Service Configuration"""
    
    # Service
    SERVICE_NAME: str = "cart_service"
    SERVICE_PORT: int = 8008
    SERVICE_HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://:dev_password_change_in_prod@localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Service URLs
    CATALOG_SERVICE_URL: str = "http://localhost:8002"
    INVENTORY_SERVICE_URL: str = "http://localhost:8007"
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ]
    
    # Cart Configuration
    MAX_CART_ITEMS: int = 100
    MAX_QUANTITY_PER_ITEM: int = 1000
    CART_TTL_HOURS: int = 72  # Cart expires after 72 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

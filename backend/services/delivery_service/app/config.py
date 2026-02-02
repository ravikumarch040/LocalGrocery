"""Delivery Service configuration"""
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
    SERVICE_NAME: str = "delivery-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Order Service
    ORDER_SERVICE_URL: str = "http://localhost:8003"
    
    # Maps & Routes
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # Delivery settings
    MAX_DELIVERY_RADIUS_KM: float = 10.0  # Maximum delivery distance in km
    DELIVERY_PARTNER_SEARCH_RADIUS_KM: float = 5.0  # Search radius for available riders
    AVERAGE_SPEED_KMH: float = 20.0  # Average delivery speed for ETA calculation
    
    # Delivery fees
    BASE_DELIVERY_FEE: float = 20.0  # Base delivery fee in INR
    PER_KM_FEE: float = 5.0  # Additional fee per km
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

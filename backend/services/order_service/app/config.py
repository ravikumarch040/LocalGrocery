"""Configuration for Order Service"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Service settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://localgrocery:dev_password_change_in_prod@localhost:5432/localgrocery"
    
    # Service ports & URLs
    auth_service_url: str = "http://localhost:8001"
    catalog_service_url: str = "http://localhost:8002"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-prod"
    jwt_algorithm: str = "HS256"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


settings = get_settings()

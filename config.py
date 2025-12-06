"""
Configuration settings for Notification Service
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "Notification Service"
    app_version: str = "1.0.0"
    environment: str = "dev"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    
    # Firestore settings
    firestore_project_id: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


class DevSettings(Settings):
    """Development settings"""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    environment: str = "dev"
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        case_sensitive=False,
        extra="ignore"
    )


class ProductionSettings(Settings):
    """Production settings"""
    debug: bool = False
    environment: str = "production"
    log_level: str = "WARNING"
    reload: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        case_sensitive=False,
        extra="ignore"
    )


def get_settings_class():
    """Get settings class based on environment"""
    env = os.getenv("APP_ENV", "dev").lower()
    settings_map = {
        "dev": DevSettings,
        "local": DevSettings, # Keep local mapped to dev for backward compatibility if needed, or just remove. User said default dev.
        "production": ProductionSettings,
        "prod": ProductionSettings
    }
    return settings_map.get(env, DevSettings)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings_class = get_settings_class()
    return settings_class()

"""
Configuration settings for Teams Notification Service
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "Teams Notification Service"
    app_version: str = "1.0.0"
    environment: str = "local"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    
    # Microsoft Teams Notification settings
    teams_webhook_url: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


class LocalSettings(Settings):
    """Local development settings"""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    environment: str = "local"
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
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
    env = os.getenv("ENVIRONMENT", "local").lower()
    settings_map = {
        "local": LocalSettings,
        "production": ProductionSettings,
        "prod": ProductionSettings
    }
    return settings_map.get(env, LocalSettings)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings_class = get_settings_class()
    return settings_class()

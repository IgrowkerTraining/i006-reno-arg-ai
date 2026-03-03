<<<<<<< HEAD
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Backend IA - RENO Studio CPS"
    debug_mode: bool = True
    
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/reno_db",
        alias="DATABASE_URL"
    )
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    max_tokens: int = 2000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def available_models(self) -> list[str]:
        """Devuelve la lista completa de modelos del registro generado."""
        try:
            from app.config.models_registry import AVAILABLE_MODELS
            return AVAILABLE_MODELS if AVAILABLE_MODELS else ["google/gemma-3-27b-it:free"]
        except ImportError:
            return ["google/gemma-3-27b-it:free"]

settings = Settings()
=======
"""Application settings and configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    app_name: str = "FastAPI AI Template"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
>>>>>>> origin/develop

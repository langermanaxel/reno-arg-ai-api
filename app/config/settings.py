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
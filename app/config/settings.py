from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import logging

class Settings(BaseSettings):
    # --- App Info ---
    PROJECT_NAME: str = "AI Construction Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False # Útil para mostrar/ocultar errores detallados

    # --- Security & DB ---
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # --- CORS ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Logging ---
    # Permite cambiar a DEBUG, INFO, WARNING o ERROR desde el .env
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def LOGGING_LEVEL(self):
        """Convierte el string de LOG_LEVEL en un nivel real de la librería logging."""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

settings = Settings()
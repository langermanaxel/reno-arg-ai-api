from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import logging

class Settings(BaseSettings):
    # --- App Info ---
    PROJECT_NAME: str = "AI Construction Analysis API"
    VERSION: str = "1.0.0"
    ENV: str = "development"
    ADMIN_SECRET_TOKEN: str  # Se leerá del .env
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # --- Security & DB ---
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # --- CORS ---
    CORS_ORIGINS: List[str] = ["*"]

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Configuración de Pydantic v2 (ÚNICA FUENTE) ---
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False, # Ayuda a que lea DATABASE_URL aunque en el .env esté en minúsculas
        extra="ignore"
    )

    @property
    def LOGGING_LEVEL(self):
        """Convierte el string de LOG_LEVEL en un nivel real de la librería logging."""
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)

settings = Settings()
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Backend IA - RENO Studio CPS"
    debug_mode: bool = True
    
    # Base de datos (se toma de ENV o usa el default local)
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/reno_db",
        alias="DATABASE_URL"
    )
    
    # Configuración LLM
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    max_tokens: int = 2000
    
    # Pydantic Settings leerá el .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variables extra en el .env
    )

    @property
    def llm_model(self) -> str:
        """
        Obtiene dinámicamente el modelo preferido del registro generado.
        Si el archivo no existe o falla, devuelve un fallback seguro.
        """
        try:
            from app.config.models_registry import AVAILABLE_MODELS
            return AVAILABLE_MODELS[0] if AVAILABLE_MODELS else "google/gemma-3-27b-it:free"
        except ImportError:
            return "google/gemma-3-27b-it:free"

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Definimos las variables y pydantic las validará al arrancar
    PROJECT_NAME: str = "AI Construction Analysis"
    VERSION: str = "3.2.0"
    
    # Base de Datos
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    
    # IA
    OPENROUTER_API_KEY: str = Field(..., alias="OPENROUTER_API_KEY")
    
    # Seguridad (la usaremos luego)
    SECRET_KEY: str = "cambiame_por_algo_seguro_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variables extra en el .env que no usemos aquí
    )

# Instancia global para usar en todo el proyecto
settings = Settings()
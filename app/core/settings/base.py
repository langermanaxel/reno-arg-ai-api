"""Settings principal Pydantic."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from enum import Enum
from pathlib import Path
from ..utils.enums import EnvEnum, LogLevelEnum, SecurityAlgorithmEnum
import logging


class Settings(BaseSettings):
    # APP INFO
    PROJECT_NAME: str = "AI Construction Analysis API"
    VERSION: str = "1.0.0"
    ENV: EnvEnum = EnvEnum.DEVELOPMENT
    ADMIN_SECRET_TOKEN: str
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # DATABASE
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # OPENROUTER
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL_DEFAULT: str = "gpt-4o-mini"

    # SECURITY
    SECURITY_ALGORITHM: SecurityAlgorithmEnum = SecurityAlgorithmEnum.BCRYPT
    BCRYPT_ROUNDS: int = 12
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS + LOGGING + WEBHOOK
    CORS_ORIGINS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.INFO
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
        validate_assignment=True,
    )

    @property
    def LOGGING_LEVEL(self) -> int:
        return getattr(logging, self.LOG_LEVEL, logging.INFO)

    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.ENV == EnvEnum.DEVELOPMENT

    @property
    def DATABASE_ECHO(self) -> bool:
        return self.IS_DEVELOPMENT

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return ["*"] if self.CORS_ORIGINS == ["*"] else [o.strip() for o in self.CORS_ORIGINS]

    @property
    def LOG_DIR(self) -> Path:
        return Path("logs")


settings = Settings()


def validate_settings() -> Settings:
    """Valida y retorna la instancia de settings."""
    return settings
"""Core utilities - fácil importación."""

from .settings import settings, validate_settings
from .logging import setup_logging, get_logger

# 1. Create the instance here so it can be imported elsewhere
logger = get_logger("app") 

from .security import (
    get_password_hash, verify_password, needs_rehash,
    generate_password, is_password_strong
)
from .utils.enums import EnvEnum, LogLevelEnum, SecurityAlgorithmEnum

__all__ = [
    "logger",             # 2. Add "logger" to this list
    "settings", "validate_settings",
    "setup_logging", "get_logger",
    "get_password_hash", "verify_password",
    "EnvEnum", "LogLevelEnum", "SecurityAlgorithmEnum",
    "needs_rehash", "generate_password", "is_password_strong"
]
"""Enums compartidos."""

from enum import Enum

class EnvEnum(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SecurityAlgorithmEnum(str, Enum):
    BCRYPT = "bcrypt"
    ARGON2 = "argon2"
    SCRYPT = "scrypt"

"""Password context dinámico."""

from passlib.context import CryptContext
from app.core.settings.base import settings
from app.core.logging.setup import get_logger

logger = get_logger("security")

def get_password_context() -> CryptContext:
    """Context según entorno."""
    schemes = ["bcrypt"]
    if settings.ENV == "production":
        schemes.insert(0, "argon2")
    if settings.SECURITY_ALGORITHM == "scrypt":
        schemes.insert(0, "scrypt")
    
    context = CryptContext(
        schemes=schemes,
        bcrypt__rounds=settings.BCRYPT_ROUNDS,
        argon2__time_cost=settings.ARGON2_TIME_COST,
        argon2__memory_cost=settings.ARGON2_MEMORY_COST,
        argon2__parallelism=settings.ARGON2_PARALLELISM,
        deprecated="auto",
        cache_frames=1,
    )
    
    logger.debug(f"🔐 Context: {schemes[0]} (rounds: {settings.BCRYPT_ROUNDS})")
    return context

_password_context = None

def get_global_pwd_context() -> CryptContext:
    """Singleton lazy."""
    global _password_context
    if _password_context is None:
        _password_context = get_password_context()
    return _password_context

"""Funciones públicas de seguridad."""

import logging
import secrets
import string
from passlib.exc import UnknownHashError
from .context import get_password_context, get_global_pwd_context
from ..logging import get_logger

logger = get_logger("app.security")

def get_password_hash(password: str, legacy_context: bool = False) -> str:
    context = get_password_context() if legacy_context else get_global_pwd_context()
    hashed = context.hash(password)
    logger.debug(f"🔐 Hash: {hashed[:20]}...")
    return hashed

def verify_password(plain: str, hashed: str) -> bool:
    try:
        is_valid = get_global_pwd_context().verify(plain, hashed)
        logger.debug("✅" if is_valid else "❌") 
        return is_valid
    except UnknownHashError:
        logger.error("🔒 Hash desconocido")
        return False
    except Exception as e:
        logger.error(f"🔒 Error: {e}")
        return False

def needs_rehash(hashed: str, legacy_context: bool = False) -> bool:
    try:
        context = get_password_context() if legacy_context else get_global_pwd_context()
        return context.needs_rehash(hashed)
    except UnknownHashError:
        return True

def generate_password(min_length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(min_length))

def is_password_strong(password: str, min_length: int = 12, min_complexity: int = 3) -> bool:
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    return len(password) >= min_length and sum([has_upper, has_lower, has_digit, has_special]) >= min_complexity

"""Validación de settings."""

from app.core.settings.base import settings
from app.core.logging import get_logger

logger = get_logger("app.settings")

def validate_settings():
    """Valida configuración crítica."""
    errors = []
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL obligatoria")
    if not settings.OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY obligatoria")
    if not settings.ADMIN_SECRET_TOKEN:
        errors.append("ADMIN_SECRET_TOKEN obligatoria")
    if settings.JWT_SECRET_KEY and len(settings.JWT_SECRET_KEY) < 32:
        errors.append("JWT_SECRET_KEY ≥ 32 chars")
    
    if errors:
        raise ValueError(f"❌ Configuración inválida: {' | '.join(errors)}")
    
    logger.info(f"✅ Config: {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENV}]")

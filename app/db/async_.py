"""Async database engine."""

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.settings.base import settings
from app.core.logging import get_logger
from .base import get_async_sessionmaker

logger = get_logger(__name__)

def get_async_engine():
    """Engine asíncrono."""
    url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(
        url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DATABASE_ECHO,
    )

AsyncEngine = None
AsyncSessionLocal = None

def init_async_engine():
    """Inicializa async engine global."""
    global AsyncEngine, AsyncSessionLocal
    AsyncEngine = get_async_engine()
    AsyncSessionLocal = get_async_sessionmaker(bind=AsyncEngine)
    logger.info("⚡ Async engine inicializado")

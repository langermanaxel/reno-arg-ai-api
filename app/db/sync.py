"""Sync database engine production-ready."""

from sqlalchemy import create_engine, event
from app.core.settings.base import settings
from app.core.logging import get_logger
from .base import get_sync_sessionmaker

logger = get_logger(__name__)

def get_sync_engine():
    """Engine síncrono production-ready."""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DATABASE_ECHO,
        server_side_cursors=False,
        prepare_threshold=20,
    )
    
    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, connection_record):
        logger.debug("🔌 Nueva conexión DB sync")
    
    return engine

# Global instances
engine = None
SessionLocal = None

def init_sync_engine():
    """Inicializa sync engine global."""
    global engine, SessionLocal
    engine = get_sync_engine()
    SessionLocal = get_sync_sessionmaker(bind=engine)
    logger.info("🗄️ Sync engine inicializado")

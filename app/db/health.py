"""Database health checks e inicialización."""

from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.config import settings
from .sync import init_sync_engine, engine, SessionLocal

def init_database():
    """Inicializa database completa."""
    init_sync_engine()
    logger.info(f"📊 Pool: {settings.DATABASE_POOL_SIZE}+{settings.DATABASE_MAX_OVERFLOW}")

def check_db_connection():
    """Verifica conexión DB."""
    try:
        if not engine:
            return False
        with SessionLocal() as session:
            session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"❌ DB conexión fallida: {e}")
        return False

def create_tables():
    """Crea todas las tablas."""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas")

def drop_tables():
    """Borra todas las tablas."""
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.info("🗑️ Tablas borradas")

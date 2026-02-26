"""Database dependencies para FastAPI."""

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.db.base import Base
from app.db.sync import get_sync_engine
from app.db.health import check_db_connection
from app.core.logging import get_logger

engine = get_sync_engine()

logger = get_logger(__name__)

# ========================================
# DEPENDENCIA PRINCIPAL (Context Manager)
# ========================================
async def get_db():
    """Dependency para endpoints sync."""
    from app.db.sync import SessionLocal  # lazy import, ya inicializado en startup
    db = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except Exception:
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

# ========================================
# ASYNC DEPENDENCIA (Futuro)
# ========================================
async def get_db_async():
    """Para endpoints async."""
    from app.db.async_ import get_async_sessionmaker
    async with get_async_sessionmaker() as session:
        yield session

# ========================================
# HEALTH CHECK DEPENDENCY
# ========================================
async def get_db_health() -> bool:
    """Verifica DB para health checks."""
    if not check_db_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )
    return True

# ========================================
# CREATE/DROP TABLES
# ========================================
def create_tables():
    """Crea todas las tablas."""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas")

def drop_tables():
    """Borra todas las tablas (solo dev)."""
    Base.metadata.drop_all(bind=engine)
    logger.info("🗑️  Tablas borradas")
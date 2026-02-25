"""SQLAlchemy 2.x Base y Session factories."""

from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

class Base(DeclarativeBase):
    """Base para todos los modelos."""
    __table_args__ = {'extend_existing': True}

def get_sync_sessionmaker(bind=None):
    """Sync session factory."""
    return sessionmaker(
        bind=bind,
        class_=Session,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

def get_async_sessionmaker(bind=None):
    """Async session factory."""
    from sqlalchemy.ext.asyncio import AsyncSession
    return sessionmaker(
        bind=bind,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

"""Database package - fácil importación."""

from .base import Base, SessionLocal, engine
from .health import check_db_connection, init_database
from .deps import get_db  # Importará desde api/deps.py

__all__ = ["Base", "SessionLocal", "engine", "check_db_connection", "init_database", "get_db"]

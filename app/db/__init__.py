"""Database package - fácil importación."""

from .base import Base, get_sync_sessionmaker, get_async_sessionmaker
from .health import check_db_connection, init_database, create_tables, drop_tables
from .sync import get_sync_engine, init_sync_engine
from .async_ import get_async_engine, init_async_engine

__all__ = [
    "Base",
    "get_sync_sessionmaker",
    "get_async_sessionmaker",
    "create_tables",
    "drop_tables",  
    "check_db_connection", 
    "init_database", 
    "get_sync_engine",
    "init_sync_engine",
    "get_async_engine",
    "init_async_engine"
    ]

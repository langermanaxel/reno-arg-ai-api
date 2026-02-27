from .database import Base, SessionLocal, engine

def get_db():
    """Dependencia para obtener la sesión de DB en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Al ponerlos aquí, puedes importar directamente desde 'app.db'
__all__ = ["Base", "engine", "get_db"]
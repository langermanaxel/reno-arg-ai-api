from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión (coincide con el docker-compose)
# Estructura: postgresql://usuario:password@host:puerto/nombre_db
SQLALCHEMY_DATABASE_URL = "postgresql://admin:admin123@localhost:5432/ai_analisis_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la DB en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
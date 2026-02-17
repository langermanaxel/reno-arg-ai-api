from fastapi import FastAPI
from app.db.base import Base, engine
from app.api.v1.endpoints import analisis, usuarios

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Construction Analysis API",
    version="3.1.0",
    description="API para análisis de obras con trazabilidad LLM completa."
)

# Registramos el router bajo el prefijo /analisis
# Ya NO incluimos tags aquí para evitar la duplicidad que viste en Swagger
app.include_router(analisis.router, prefix="/analisis")
app.include_router(usuarios.router, prefix="/auth")

@app.get("/", tags=["Estado"])
def read_root():
    return {"status": "API Online 🚀", "docs": "/docs"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.core.logging import setup_logging
from app.db.base import Base, engine
# IMPORTANTE: Eliminamos 'mantenimiento' de aquí porque ya no existe como archivo
from app.api.v1.endpoints import analisis, usuarios, health

# 1. Configuración de logs profesional
setup_logging()

# 2. Sincronización de Base de Datos
# Crea las tablas en Postgres si no existen basándose en los modelos
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Evita que la app muera si la DB tarda unos segundos en arrancar
    print(f"⚠️ Error al conectar o sincronizar la DB: {e}")

# 3. Inicialización de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API profesional para análisis de obras con auditoría LLM.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 4. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Inclusión de Routers
# El router de analisis ahora incluye internamente el endpoint /reset-db
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Sistema"])
app.include_router(usuarios.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Usuarios"])
app.include_router(analisis.router, prefix=f"{settings.API_V1_STR}/analisis", tags=["Análisis y Operaciones"])

# 6. Endpoint raíz de información
@app.get("/", tags=["Sistema"])
def read_root():
    return {
        "status": "API Online 🚀", 
        "environment": settings.ENV,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
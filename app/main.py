from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importamos desde nuestra estructura modularizada
from app.config import settings
from app.routers import api_router
from app.db import engine
from app.models import init_db
from app.core.exceptions import AnalisisNotFoundError, IAProcessingError

# ═══════════════════════════════════════════════════════════════════
# 1. INICIALIZACIÓN DE FASTAPI
# ═══════════════════════════════════════════════════════════════════
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="API para procesamiento de análisis de obras con Inteligencia Artificial."
)

# ═══════════════════════════════════════════════════════════════════
# 2. CONFIGURACIÓN DE CORS (Seguridad Frontend-Backend)
# ═══════════════════════════════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ¡Ojo! En producción cambiar por los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════
# 3. EVENTOS DE CICLO DE VIDA (Startup)
# ═══════════════════════════════════════════════════════════════════
@app.on_event("startup")
def startup_event():
    """
    Se ejecuta justo antes de que el servidor empiece a recibir peticiones.
    Ideal para inicializar la base de datos.
    """
    init_db(engine)
    print(f"🚀 {settings.app_name} iniciado correctamente.")
    print(f"⚙️  Modo Debug: {settings.debug_mode}")

# ═══════════════════════════════════════════════════════════════════
# 4. MANEJO GLOBAL DE EXCEPCIONES (Core)
# ═══════════════════════════════════════════════════════════════════
@app.exception_handler(AnalisisNotFoundError)
async def analisis_not_found_handler(request: Request, exc: AnalisisNotFoundError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Not Found", "mensaje": exc.detail},
    )

@app.exception_handler(IAProcessingError)
async def ia_processing_error_handler(request: Request, exc: IAProcessingError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Internal Server Error", "mensaje": exc.detail},
    )

# ═══════════════════════════════════════════════════════════════════
# 5. REGISTRO DE RUTAS (Endpoints)
# ═══════════════════════════════════════════════════════════════════
# Incluimos el router central de app/routers/__init__.py
app.include_router(api_router, prefix="/api/v1")

# Endpoint de salud (Health Check) para monitoreo
@app.get("/health", tags=["Sistema"])
def health_check():
    """Endpoint básico para verificar que el servidor está vivo."""
    return {"status": "ok", "app": settings.app_name}
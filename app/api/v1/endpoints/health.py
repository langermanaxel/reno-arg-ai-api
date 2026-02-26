from fastapi import APIRouter, Response, status
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from pydantic import BaseModel
import time

from app.core.settings import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# ── Mejora 5: Response model explícito ────────────────────────────────────────

class ComponentStatus(BaseModel):
    status: str
    latency_ms: float | None = None  # Solo presente en "database"


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    service: str
    components: dict[str, ComponentStatus]


# ── Mejora 3: Conexión manual (no como dependencia de FastAPI) ─────────────────

def _get_engine():
    """Crea un engine desechable solo para el health check."""
    return create_engine(settings.DATABASE_URL, pool_pre_ping=False)


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response) -> HealthResponse:
    """
    Verifica el estado de la API y de la Base de Datos.
    Retorna 503 si algún componente crítico está caído.
    """
    # Mejora 2: Estado inicial directo en "up"; solo se degrada en el except
    health_status = HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",  # Mejora 4
        version=settings.VERSION,
        service=settings.PROJECT_NAME,
        components={
            "api": ComponentStatus(status="up"),
            "database": ComponentStatus(status="up"),
        },
    )

    # Mejora 3: Conexión completamente manual → cualquier fallo queda en el try/except
    # y devuelve 503 en lugar de 500
    engine = None
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            # Mejora 1: Latencia de la DB
            start = time.monotonic()
            conn.execute(text("SELECT 1"))
            latency_ms = round((time.monotonic() - start) * 1000, 2)

        health_status.components["database"] = ComponentStatus(
            status="up",
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.error("Error en Health Check de Base de Datos: %s", e)
        health_status.components["database"] = ComponentStatus(status="down")
        health_status.status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    finally:
        if engine:
            engine.dispose()

    return health_status
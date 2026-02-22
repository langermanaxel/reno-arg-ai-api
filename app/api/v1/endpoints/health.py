from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone # Modernizamos aquí
import logging

from app.api.dependencies import get_db
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check(response: Response, db: Session = Depends(get_db)):
    """
    Diagnóstico Profesional: Verifica el estado de la API y de la Base de Datos.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
        "components": {
            "api": "up",
            "database": "unknown"
        }
    }

    try:
        # Validación real contra Postgres
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "up"
    except Exception as e:
        logger.error(f"Error en Health Check de Base de Datos: {str(e)}")
        health_status["components"]["database"] = "down"
        health_status["status"] = "unhealthy"
        # Docker detectará este 503
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
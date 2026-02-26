import os
import sys
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.settings import settings
from app.db.base import Base
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/sync-models")
async def trigger_sync():
    """Sincroniza modelos desde OpenRouter."""
    try:
        sys.path.append(os.getcwd())
        from sync_models import sync_openrouter_models
        sync_openrouter_models()
        logger.info("🔄 Modelos sincronizados")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"❌ Sync falló: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-db")
async def reset_database(x_admin_token: str = Header(None), db: Session = Depends(get_db)):
    """⚠️ Reset total de DB (solo desarrollo)."""
    if settings.ENV != "development" or x_admin_token != settings.ADMIN_SECRET_TOKEN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acceso denegado")
    
    try:
        logger.warning("💣 Reset DB ejecutado")
        engine = db.get_bind()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

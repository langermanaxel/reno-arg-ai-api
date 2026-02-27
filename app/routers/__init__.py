from fastapi import APIRouter
from .analisis import router as analisis_router

# Router principal que agrupa todos los sub-routers
api_router = APIRouter()
api_router.include_router(analisis_router)

__all__ = ["api_router"]
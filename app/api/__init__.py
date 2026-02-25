from fastapi import APIRouter

from app.api.v1.endpoints import analisis, admin, health

api_router = APIRouter()
api_router.include_router(analisis.router, prefix="/analisis")
api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(health.router, prefix="/health")
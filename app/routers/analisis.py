from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db, SessionLocal
from app.schemas.analisis import AnalisisCreate, AnalisisOut
from app.schemas.snapshot import SnapshotInput
from app.services import analisis_service
from app.core.exceptions import AnalisisNotFoundError
from app.crud import crud_analisis

router = APIRouter(prefix="/analisis", tags=["Análisis de IA"])

@router.post("/", response_model=AnalisisOut, status_code=status.HTTP_201_CREATED)
def crear_solicitud_analisis(
    solicitud: AnalisisCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva solicitud de análisis en estado PENDIENTE."""
    analisis_id = analisis_service.iniciar_nuevo_analisis(db, solicitud)
    return crud_analisis.get_analisis(db, analisis_id)

@router.post("/{analisis_id}/procesar", status_code=status.HTTP_202_ACCEPTED)
def procesar_datos(
    analisis_id: UUID,
    snapshot: SnapshotInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    analisis = crud_analisis.get_analisis(db, analisis_id)
    if not analisis:
        raise AnalisisNotFoundError(str(analisis_id))

    # ✅ El background task crea y gestiona su propia sesión
    def tarea():
        db_bg = SessionLocal()
        try:
            import asyncio
            asyncio.run(
                analisis_service.procesar_snapshot_con_ia(db_bg, analisis_id, snapshot)
            )
        finally:
            db_bg.close()

    background_tasks.add_task(tarea)

    return {"mensaje": "Procesamiento de IA iniciado en segundo plano", "analisis_id": analisis_id}

@router.get("/{analisis_id}", response_model=AnalisisOut)
def obtener_analisis(
    analisis_id: UUID,
    db: Session = Depends(get_db)
):
    """Consulta el estado y los resultados de un análisis."""
    analisis = crud_analisis.get_analisis(db, analisis_id)
    if not analisis:
        raise AnalisisNotFoundError(str(analisis_id))
    return analisis
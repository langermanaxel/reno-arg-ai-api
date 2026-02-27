from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
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
    """
    Recibe el Snapshot completo del Backend Principal y envía el 
    procesamiento de IA a una tarea en segundo plano (Background Task).
    """
    analisis = crud_analisis.get_analisis(db, analisis_id)
    if not analisis:
        raise AnalisisNotFoundError(str(analisis_id))
    
    # Procesamos la IA en background para no bloquear la respuesta HTTP
    background_tasks.add_task(
        analisis_service.procesar_snapshot_con_ia, 
        db, 
        analisis_id, 
        snapshot
    )
    
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
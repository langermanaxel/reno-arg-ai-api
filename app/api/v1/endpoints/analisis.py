import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.api.dependencies import get_db
from app.schemas.snapshot import SnapshotCreate
from app.crud.analisis import AnalisisCRUD

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/iniciar")
async def iniciar_analisis(
    snapshot_in: SnapshotCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Inicia el proceso de persistencia y análisis con IA."""
    crud = AnalisisCRUD(db)
    
    try:
        analisis = crud.crear_registro_padre(snapshot_in.proyecto_codigo)
        snapshot = crud.persistir_snapshot(analisis.id, snapshot_in.datos)
        crud.persistir_datos_obra(snapshot.id, snapshot_in.datos)
        db.commit()
        
        await crud.procesar_con_ia(analisis.id, snapshot_in.datos)
        analisis.estado = "COMPLETADO"
        db.commit()
        
        background_tasks.add_task(crud.notificar_webhook, analisis.id, analisis.proyecto_codigo)
        
        logger.info(f"✅ Análisis completado: {analisis.id}")
        return {"analisis_id": analisis.id}
        
    except Exception as e:
        db.rollback()
        if 'analisis' in locals():
            analisis.estado = "ERROR"
            db.commit()
        logger.error(f"❌ Error análisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detalle/{analisis_id}")
async def obtener_analisis_completo(analisis_id: str, db: Session = Depends(get_db)):
    """Obtiene radiografía completa del análisis."""
    crud = AnalisisCRUD(db)
    resultado = crud.get_analisis_completo(analisis_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return resultado

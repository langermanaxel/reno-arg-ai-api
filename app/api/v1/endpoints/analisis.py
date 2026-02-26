from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.snapshot import SnapshotCreate
from app.crud.analisis import AnalisisCRUD
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

async def procesar_analisis_bg(analisis_id: str, datos: dict):
    """
    Tarea asíncrona de fondo. 
    Usa await para el LLM y un bloque 'with' para la sesión síncrona de DB.
    """
    from app.crud.llm import LLMProcessor
    from app.db.sync import SessionLocal 
    from app.crud.analisis import AnalisisCRUD

    # IMPORTANTE: Creamos la sesión dentro del proceso de fondo
    with SessionLocal() as db:
        try:
            logger.info(f"⚙️ Iniciando procesamiento IA para ID: {analisis_id}")
            processor = LLMProcessor(db)
            
            # ✅ CORRECCIÓN: Ahora sí esperamos a la corrutina
            await processor.procesar_con_ia(analisis_id, datos)
            
            logger.info(f"✅ Análisis {analisis_id} finalizado con éxito")
        except Exception as e:
            logger.error(f"❌ Error crítico en procesamiento: {e}")
            try:
                # Usamos la misma sesión 'db' para persistir el error
                crud = AnalisisCRUD(db)
                crud.marcar_error(analisis_id, str(e))
                db.commit()
            except Exception as db_err:
                logger.error(f"No se pudo marcar el error en DB: {db_err}")

@router.post("/iniciar", status_code=202)
async def iniciar_analisis(
    snapshot_in: SnapshotCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    crud = AnalisisCRUD(db)
    try:
        # 1. Registro inicial en la DB principal del request
        analisis = crud.crear_registro_padre(snapshot_in.proyecto_codigo)
        db.commit()
        db.refresh(analisis)
        
        analisis_id_str = str(analisis.id)
        
        # 2. Encolar la tarea síncrona
        # FastAPI detecta que no es 'async def' y la manda al threadpool por ti
        background_tasks.add_task(
            procesar_analisis_bg, 
            analisis_id_str, 
            snapshot_in.datos
        )
        
        return {
            "analisis_id": analisis_id_str,
            "status": "processing"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error al iniciar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detalle/{analisis_id}")
async def obtener_analisis_completo(analisis_id: str, db: Session = Depends(get_db)):
    crud = AnalisisCRUD(db)
    resultado = crud.get_analisis_completo(analisis_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return resultado
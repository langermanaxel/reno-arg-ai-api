from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.snapshot import SnapshotCreate
from app.crud.analisis import AnalisisCRUD
from app.crud.queries import get_analisis_completo
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


async def procesar_analisis_bg(
    analisis_id: str,
    datos: dict,
    model: str | None,
    temperature: float,
    system_prompt: str | None,
    instrucciones_extra: str | None,
):
    from app.crud.llm import LLMProcessor
    from app.db.sync import SessionLocal

    with SessionLocal() as db:
        crud = AnalisisCRUD(db)  # ← fuera del try
        try:
            logger.info(f"⚙️ Iniciando procesamiento IA para ID: {analisis_id}")
            crud.guardar_snapshot(analisis_id, datos)

            await crud.llm_processor.procesar_con_ia(
                analisis_id=analisis_id,
                datos=datos,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
                instrucciones_extra=instrucciones_extra,
            )

            crud.marcar_completado(analisis_id)
            db.commit()
            logger.info(f"✅ Análisis {analisis_id} finalizado con éxito")

        except Exception as e:
            logger.error(f"❌ Error crítico en procesamiento: {e}", exc_info=True)
            try:
                crud.marcar_error(analisis_id, str(e))
                db.commit()
            except Exception as db_err:
                logger.error(f"No se pudo marcar el error en DB: {db_err}")


@router.post("/iniciar", status_code=202)
async def iniciar_analisis(
    snapshot_in: SnapshotCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    crud = AnalisisCRUD(db)
    try:
        # 1. Registro inicial en DB
        analisis = crud.crear_registro_padre(snapshot_in.proyecto_codigo)
        db.commit()
        db.refresh(analisis)

        analisis_id_str = str(analisis.id)

        # 2. Encolar tarea de fondo con todos los parámetros LLM
        # procesar_analisis_bg es async def → corre en el event loop (no en threadpool)
        background_tasks.add_task(
            procesar_analisis_bg,
            analisis_id_str,
            snapshot_in.datos,
            snapshot_in.model,
            snapshot_in.temperature,
            snapshot_in.system_prompt,
            snapshot_in.instrucciones_extra,
        )

        return {
            "analisis_id": analisis_id_str,
            "status": "processing",
            "model": snapshot_in.model or "fallback",
            "temperature": snapshot_in.temperature,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error al iniciar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detalle/{analisis_id}")
async def obtener_analisis_completo(
    analisis_id: str,
    db: Session = Depends(get_db),
):
    resultado = get_analisis_completo(db, analisis_id)

    if not resultado:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return resultado
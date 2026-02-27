import logging
from sqlalchemy.orm import Session
from uuid import UUID

from app.schemas.analisis import AnalisisCreate
from app.schemas.snapshot import SnapshotInput
from app.crud import crud_analisis
from app.models.enums import EstadoAnalisis
from app.utils.hashing import generar_hash_payload
from app.core.exceptions import AnalisisNotFoundError
from app.services.ai_engine import AIEngineService

logger = logging.getLogger("analisis_service")

def iniciar_nuevo_analisis(db: Session, datos: AnalisisCreate) -> UUID:
    """Crea el registro inicial del análisis"""
    nuevo_analisis = crud_analisis.create_analisis(db, datos)
    return nuevo_analisis.id

async def procesar_snapshot_con_ia(db: Session, analisis_id: UUID, snapshot: SnapshotInput):
    """
    Orquestador que coordina el flujo de datos y la IA.
    """
    analisis = crud_analisis.get_analisis(db, analisis_id)
    if not analisis:
        logger.error(f"Análisis {analisis_id} no encontrado.")
        return

    crud_analisis.update_estado(db, analisis_id, EstadoAnalisis.PROCESANDO)

    try:
        # ✅ CORRECCIÓN: Usar mode='json' para que las fechas sean strings antes del hash
        snapshot_serializable = snapshot.model_dump(mode='json')
        payload_hash = generar_hash_payload(snapshot_serializable)
        
        logger.info(f"Procesando snapshot {analisis_id} con hash: {payload_hash}")

        # Invocación al Motor de IA
        ai_engine = AIEngineService(db)
        await ai_engine.procesar_analisis_completo(analisis_id, snapshot)

    except Exception as e:
        # ✅ CORRECCIÓN: Usar str(e) para evitar errores de serialización en el log
        error_msg = str(e)
        logger.error(f"Error crítico en la orquestación del análisis {analisis_id}: {error_msg}")
        
        # Aseguramos que el estado cambie a ERROR en la DB
        crud_analisis.update_estado(db, analisis_id, EstadoAnalisis.ERROR)
        db.commit()
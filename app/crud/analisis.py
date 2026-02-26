"""AnalisisCRUD principal - Orquesta el flujo completo."""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from .snapshot import SnapshotRepository
from .llm import LLMProcessor
from .webhook import WebhookNotifier
from app.models import Analisis, EstadoAnalisis
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalisisCRUD:
    def __init__(self, db: Session):
        self.db = db
        self.snapshot_repo = SnapshotRepository(db)
        self.llm_processor = LLMProcessor(db)
        self.webhook_notifier = WebhookNotifier(db)

    def crear_registro_padre(self, proyecto_codigo: str) -> Analisis:
        """Crea registro Analisis padre en estado PROCESANDO."""
        analisis = Analisis(
            proyecto_codigo=proyecto_codigo,
            estado=EstadoAnalisis.PROCESANDO,
        )
        self.db.add(analisis)
        self.db.flush()
        logger.info(f"📊 Analisis creado: {analisis.id}")
        return analisis

    def guardar_snapshot(self, analisis_id: str, datos: Dict[str, Any]):
        """
        Persiste el snapshot recibido en las tablas normalizadas.
        Llamar antes de iniciar el procesamiento IA para que
        datos_obra.proyecto no quede null en el GET /detalle.
        """
        self.snapshot_repo.persistir_snapshot_completo(analisis_id, datos)
        self.db.commit()
        logger.info(f"💾 Snapshot persistido para análisis: {analisis_id}")

    def marcar_error(self, analisis_id: str, mensaje_error: str):
        """Marca el análisis como fallido."""
        analisis = self.db.query(Analisis).filter(Analisis.id == analisis_id).first()
        if analisis:
            analisis.estado = EstadoAnalisis.ERROR
            self.db.add(analisis)
            logger.warning(f"⚠️ Análisis {analisis_id} marcado como ERROR: {mensaje_error}")

    def marcar_completado(self, analisis_id: str):
        """Marca el análisis como completado."""
        analisis = self.db.query(Analisis).filter(Analisis.id == analisis_id).first()
        if analisis:
            analisis.estado = EstadoAnalisis.COMPLETADO
            self.db.add(analisis)
            logger.info(f"✅ Análisis {analisis_id} marcado como COMPLETADO")

    async def procesar_analisis_completo(
        self,
        proyecto_codigo: str,
        datos: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None,
        instrucciones_extra: Optional[str] = None,
    ) -> str:
        """
        Flujo completo autónomo: snapshot → IA → estado → webhook.
        Usado cuando el caller quiere delegar todo en un solo método.
        """
        analisis = self.crear_registro_padre(proyecto_codigo)

        self.snapshot_repo.persistir_snapshot_completo(analisis.id, datos)
        self.db.commit()

        try:
            await self.llm_processor.procesar_con_ia(
                analisis_id=analisis.id,
                datos=datos,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
                instrucciones_extra=instrucciones_extra,
            )
            analisis.estado = EstadoAnalisis.COMPLETADO
            self.db.commit()

            await self.webhook_notifier.notificar(analisis.id, proyecto_codigo)

        except Exception as e:
            self.db.rollback()
            self.marcar_error(str(analisis.id), str(e))
            self.db.commit()
            raise

        return str(analisis.id)
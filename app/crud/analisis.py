"""AnalisisCRUD principal - Orquesta el flujo completo."""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import uuid # Útil para manejar los IDs si vienen como string
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
        """Crea registro Analisis padre."""
        analisis = Analisis(
            proyecto_codigo=proyecto_codigo, 
            estado=EstadoAnalisis.PROCESANDO
        )
        self.db.add(analisis)
        self.db.flush()
        logger.info(f"📊 Analisis creado: {analisis.id}")
        return analisis

    # --- NUEVO MÉTODO PARA MANEJO DE ERRORES ---
    def marcar_error(self, analisis_id: str, mensaje_error: str):
        """Marca el análisis como fallido en la base de datos."""
        analisis = self.db.query(Analisis).filter(Analisis.id == analisis_id).first()
        if analisis:
            analisis.estado = EstadoAnalisis.ERROR
            # Si tienes un campo para logs de error en tu modelo, úsalo aquí:
            # analisis.error_detalle = mensaje_error 
            self.db.add(analisis)
            logger.warning(f"⚠️ Estado de análisis {analisis_id} cambiado a ERROR")

    async def procesar_analisis_completo(self, proyecto_codigo: str, datos: Dict[str, Any]):
        """Flujo completo: snapshot → IA → webhook."""
        # 1. Crear registro
        analisis = self.crear_registro_padre(proyecto_codigo)
        
        # 2. Persistir snapshot + datos
        self.snapshot_repo.persistir_snapshot_completo(analisis.id, datos)
        self.db.commit()
        
        try:
            # 3. Procesar IA
            await self.llm_processor.procesar_con_ia(analisis.id, datos)
            analisis.estado = EstadoAnalisis.COMPLETADO
            self.db.commit()
            
            # 4. Notificar
            await self.webhook_notifier.notificar(analisis.id, proyecto_codigo)
        except Exception as e:
            self.db.rollback()
            self.marcar_error(str(analisis.id), str(e))
            self.db.commit()
            raise e
        
        return analisis.id
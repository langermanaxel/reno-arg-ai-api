"""Repository para snapshots y datos estructurados."""

import json
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.models import SnapshotRecibido
from app.utils.mappers import DatosMapper
from app.core.logging import get_logger

logger = get_logger(__name__)


class SnapshotRepository:
    def __init__(self, db: Session):
        self.db = db
        self.mapper = DatosMapper()

    def persistir_snapshot_completo(self, analisis_id: Any, datos: Dict[str, Any]):
        """Persiste snapshot + todos los datos desnormalizados."""

        # Si la columna es JSON nativo en SQLAlchemy, pasar el dict directamente.
        # Si es Text, usar json.dumps(datos). Ajustar según el modelo.
        snapshot = SnapshotRecibido(
            analisis_id=analisis_id,
            payload_completo=json.dumps(datos, ensure_ascii=False),  # ← serializar explícitamente
        )
        self.db.add(snapshot)
        self.db.flush()

        self._persistir_datos_obra(snapshot.id, datos)
        logger.info(f"💾 Snapshot persistido: {snapshot.id} para análisis: {analisis_id}")

    def _persistir_datos_obra(self, snapshot_id: Any, datos: Dict[str, Any]):
        """Persiste datos desnormalizados con validación defensiva."""

        # Proyecto — obligatorio
        proyecto = self.mapper.map_proyecto(snapshot_id, datos)
        if proyecto:
            self.db.add(proyecto)
        else:
            logger.warning(f"⚠️ No se pudo mapear proyecto para snapshot: {snapshot_id}")

        # Etapas — opcional
        etapas = self.mapper.map_etapas(snapshot_id, datos.get("etapas", []))
        if etapas:
            self.db.add_all(etapas)

        # Avances — opcional
        avances = self.mapper.map_avances(snapshot_id, datos.get("registros_avance", []))
        if avances:
            self.db.add_all(avances)

        # Seguridad — opcional
        seguridad = self.mapper.map_seguridad(snapshot_id, datos.get("medidas_seguridad", []))
        if seguridad:
            self.db.add(seguridad)

        self.db.flush()
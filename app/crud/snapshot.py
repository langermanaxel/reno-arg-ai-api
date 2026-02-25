"""Repository para snapshots y datos estructurados."""

import json
import logging
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models import SnapshotRecibido
from app.utils.mappers import DatosMapper

logger = logging.getLogger(__name__)

class SnapshotRepository:
    def __init__(self, db: Session):
        self.db = db
        self.mapper = DatosMapper()

    def persistir_snapshot_completo(self, analisis_id: int, datos: Dict[str, Any]):
        """Persiste snapshot + todos los datos desnormalizados."""
        # Snapshot principal
        snapshot = SnapshotRecibido(
            analisis_id=analisis_id,
            payload_completo=json.dumps(datos)
        )
        self.db.add(snapshot)
        self.db.flush()
        
        # Datos estructurados
        self._persistir_datos_obra(snapshot.id, datos)
        logger.info(f"💾 Snapshot persistido: {snapshot.id}")

    def _persistir_datos_obra(self, snapshot_id: int, datos: Dict[str, Any]):
        """Persiste datos desnormalizados."""
        self.db.add(self.mapper.map_proyecto(snapshot_id, datos))
        self.db.add_all(self.mapper.map_etapas(snapshot_id, datos.get("etapas", [])))
        self.db.add_all(self.mapper.map_avances(snapshot_id, datos.get("registros_avance", [])))
        
        seguridad = self.mapper.map_seguridad(snapshot_id, datos.get("medidas_seguridad", []))
        if seguridad:
            self.db.add(seguridad)

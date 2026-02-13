from sqlalchemy.orm import Session
from app.models.analisis import Analisis, SnapshotRecibido, EstadoAnalisis
from app.schemas.snapshot import SnapshotCreate
import json

class AnalisisService:
    def __init__(self, db: Session):
        self.db = db

    def crear_analisis(self, datos: SnapshotCreate) -> Analisis:
        # 1. Crear la entidad Analisis
        nuevo_analisis = Analisis(
            proyecto_codigo=datos.proyecto.proyecto_codigo,
            estado=EstadoAnalisis.PENDIENTE
        )
        self.db.add(nuevo_analisis)
        self.db.flush() # Para obtener el ID generado

        # 2. Guardar el Snapshot (Inmutabilidad)
        # Convertimos el objeto Pydantic a JSON string para guardarlo
        payload_str = json.dumps(datos.model_dump(), default=str)
        
        snapshot = SnapshotRecibido(
            analisis_id=nuevo_analisis.id,
            payload_completo=payload_str
        )
        self.db.add(snapshot)
        
        # 3. Commit de la transacción
        self.db.commit()
        self.db.refresh(nuevo_analisis)
        
        return nuevo_analisis
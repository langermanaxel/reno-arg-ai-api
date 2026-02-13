import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class EstadoAnalisis(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"

class Analisis(Base):
    __tablename__ = "analisis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_codigo = Column(String, index=True)
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    estado = Column(Enum(EstadoAnalisis), default=EstadoAnalisis.PENDIENTE)
    
    # Relación
    snapshot = relationship("SnapshotRecibido", back_populates="analisis", uselist=False)

class SnapshotRecibido(Base):
    __tablename__ = "snapshot_recibido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    payload_completo = Column(Text) # Usamos Text para JSONs largos
    recibido_at = Column(DateTime, default=datetime.utcnow)

    analisis = relationship("Analisis", back_populates="snapshot")
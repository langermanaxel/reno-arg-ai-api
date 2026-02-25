"""Modelos principales de análisis."""

from sqlalchemy import Column, String, Enum, ForeignKey, Boolean, Float, Index, UUID, Text
from sqlalchemy.orm import relationship

from app.models.core import (
    Base, UUIDMixin, TimestampMixin, EstadoAnalisis
)
from app.models.datos import ResultadoAnalisis, ObservacionGenerada
from app.models.auditoria import InvocacionLLM

class Analisis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "analisis"
    
    proyecto_codigo = Column(String(50), index=True, nullable=False)
    estado = Column(Enum(EstadoAnalisis), 
                   default=EstadoAnalisis.PENDIENTE, 
                   index=True)
    
    __table_args__ = (
        Index('ix_analisis_proyecto_estado', 'proyecto_codigo', 'estado'),
    )
    
    # Relaciones
    snapshot = relationship("SnapshotRecibido", back_populates="analisis", uselist=False)
    resultado = relationship("ResultadoAnalisis", back_populates="analisis", uselist=False)
    invocaciones = relationship("InvocacionLLM", back_populates="analisis")

class SnapshotRecibido(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "snapshot_recibido"
    
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"), index=True)
    payload_completo = Column(Text, nullable=False)
    
    # Relaciones
    analisis = relationship("Analisis", back_populates="snapshot")
    proyecto = relationship("DatoProyecto", back_populates="snapshot", uselist=False)
    etapas = relationship("DatoEtapa", back_populates="snapshot")
    avances = relationship("DatoAvance", back_populates="snapshot")
    seguridad = relationship("DatoSeguridad", back_populates="snapshot", uselist=False)

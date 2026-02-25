"""Datos operativos de etapas y avances."""

from sqlalchemy import Column, String, Float, Boolean, JSON, Date, ForeignKey, Index, CheckConstraint, Integer, UUID, Enum
from sqlalchemy.orm import relationship
from app.models.core import Base
from app.models.core import EstadoEtapa

class DatoEtapa(Base):
    __tablename__ = "dato_etapa"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"), index=True)
    nombre = Column(String(150), nullable=False)
    estado = Column(Enum(EstadoEtapa), nullable=False)
    avance_estimado = Column(Float, CheckConstraint('avance_estimado >= 0 AND avance_estimado <= 100'))
    
    __table_args__ = (Index('ix_dato_etapa_snapshot_estado', 'snapshot_id', 'estado'),)
    snapshot = relationship("SnapshotRecibido", back_populates="etapas")

class DatoAvance(Base):
    __tablename__ = "dato_avance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"), index=True)
    fecha_registro = Column(Date, index=True)
    supervisor = Column(String(150))
    porcentaje_avance = Column(Float, CheckConstraint('porcentaje_avance >= 0 AND porcentaje_avance <= 100'))
    presenta_desvios = Column(Boolean, default=False)
    tareas_ejecutadas = Column(JSON)
    oficios_activos = Column(JSON)
    
    snapshot = relationship("SnapshotRecibido", back_populates="avances")

class DatoSeguridad(Base):
    __tablename__ = "dato_seguridad"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"), index=True, unique=True)
    fecha_registro = Column(Date, index=True)
    medidas_implementadas = Column(JSON, nullable=False)
    total_medidas_chequeadas = Column(Integer, default=0, index=True)
    cumple_todas = Column(Boolean, default=False, index=True)
    
    snapshot = relationship("SnapshotRecibido", back_populates="seguridad")

"""Datos desnormalizados del proyecto."""

from sqlalchemy import Column, String, Float, Boolean, JSON, Date, ForeignKey, Index, CheckConstraint, UUID, Text, Enum, Integer
from sqlalchemy.orm import relationship
from app.models.core import Base, UUIDMixin, TimestampMixin
from app.models.core import EstadoEtapa, NivelRiesgo

# NOTA: HE ELIMINADO LA IMPORTACIÓN DE SnapshotRecibido DESDE AQUÍ
# SQLAlchemy resolverá el nombre "SnapshotRecibido" dinámicamente gracias al string en la relación.

class ResultadoAnalisis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "resultado_analisis"
    
    # Si 'analisis.id' está en otro archivo, SQLAlchemy lo encontrará por el nombre de la tabla
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"), unique=True, index=True)
    resumen_general = Column(Text)
    score_coherencia = Column(Float, CheckConstraint('score_coherencia >= 0 AND score_coherencia <= 1'))
    detecta_riesgos = Column(Boolean, default=False, index=True)
    
    analisis = relationship("Analisis", back_populates="resultado")
    observaciones = relationship("ObservacionGenerada", back_populates="resultado")

class ObservacionGenerada(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "observacion_generada"
    
    resultado_id = Column(UUID(as_uuid=True), ForeignKey("resultado_analisis.id"), index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    nivel = Column(Enum(NivelRiesgo), nullable=False, index=True)
    
    resultado = relationship("ResultadoAnalisis", back_populates="observaciones")

class DatoProyecto(Base):
    __tablename__ = "dato_proyecto"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"), index=True)
    codigo = Column(String(50), index=True)
    nombre = Column(String(300), nullable=False)
    responsable_tecnico = Column(String(150))
    
    # Aquí usamos el string "SnapshotRecibido" para evitar el import circular
    snapshot = relationship("SnapshotRecibido", back_populates="proyecto")
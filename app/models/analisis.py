import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Float, Boolean
from sqlalchemy import Integer, Date, JSON
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
    
    # Relaciones
    # uselist=False indica que es una relación 1 a 1
    snapshot = relationship("SnapshotRecibido", back_populates="analisis", uselist=False)
    resultado = relationship("ResultadoAnalisis", back_populates="analisis", uselist=False)

class SnapshotRecibido(Base):
    __tablename__ = "snapshot_recibido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    payload_completo = Column(Text) 
    recibido_at = Column(DateTime, default=datetime.utcnow)

    analisis = relationship("Analisis", back_populates="snapshot")

class ResultadoAnalisis(Base):
    __tablename__ = "resultado_analisis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"), unique=True)
    resumen_general = Column(Text)
    score_coherencia = Column(Float)
    detecta_riesgos = Column(Boolean, default=False)
    generado_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    analisis = relationship("Analisis", back_populates="resultado")
    observaciones = relationship("ObservacionGenerada", back_populates="resultado")

class ObservacionGenerada(Base):
    __tablename__ = "observacion_generada"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resultado_id = Column(UUID(as_uuid=True), ForeignKey("resultado_analisis.id"))
    titulo = Column(String)
    descripcion = Column(Text)
    nivel = Column(String) # INFORMATIVO, ATENCION, CRITICO
    
    resultado = relationship("ResultadoAnalisis", back_populates="observaciones")

class DatoProyecto(Base):
    __tablename__ = "dato_proyecto"
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    codigo = Column(String)
    nombre = Column(String)
    responsable_tecnico = Column(String)

class DatoEtapa(Base):
    __tablename__ = "dato_etapa"
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    nombre = Column(String)
    estado = Column(String)
    avance_estimado = Column(Integer)
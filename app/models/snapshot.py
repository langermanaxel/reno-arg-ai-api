from sqlalchemy import Column, String, Date, DateTime, Integer, Numeric, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db import Base

class SnapshotRecibido(Base):
    __tablename__ = "snapshots_recibidos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, unique=True)
    payload_completo = Column(JSON, nullable=False)
    hash_payload = Column(Integer, nullable=False, index=True)
    recibido_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    analisis = relationship("Analisis", back_populates="snapshot")
    dato_proyecto = relationship("DatoProyecto", back_populates="snapshot", uselist=False, cascade="all, delete-orphan")
    datos_etapas = relationship("DatoEtapa", back_populates="snapshot", cascade="all, delete-orphan")
    datos_avances = relationship("DatoAvance", back_populates="snapshot", cascade="all, delete-orphan")
    datos_seguridad = relationship("DatoSeguridad", back_populates="snapshot", cascade="all, delete-orphan")
    datos_validaciones = relationship("DatoValidacion", back_populates="snapshot", cascade="all, delete-orphan")

class DatoProyecto(Base):
    __tablename__ = "datos_proyectos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots_recibidos.id", ondelete="CASCADE"), nullable=False, unique=True)
    proyecto_codigo = Column(String(50), nullable=False, index=True)
    proyecto_nombre = Column(String(200), nullable=False)
    ubicacion = Column(String(200), nullable=False)
    tipo_intervencion = Column(String(100), nullable=False)
    superficie_m2 = Column(Numeric(10, 2), nullable=False)
    sistema_constructivo = Column(String(100), nullable=False)
    responsable_tecnico_nombre = Column(String(200), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    snapshot = relationship("SnapshotRecibido", back_populates="dato_proyecto")

class DatoEtapa(Base):
    __tablename__ = "datos_etapas"
    __table_args__ = (Index('ix_datos_etapas_snapshot_orden', 'snapshot_id', 'etapa_orden'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots_recibidos.id", ondelete="CASCADE"), nullable=False)
    etapa_nombre = Column(String(100), nullable=False)
    etapa_orden = Column(Integer, nullable=False)
    fecha_inicio_estimada = Column(Date, nullable=True)
    fecha_fin_estimada = Column(Date, nullable=True)
    estado = Column(String(50), nullable=False)
    snapshot = relationship("SnapshotRecibido", back_populates="datos_etapas")

class DatoAvance(Base):
    __tablename__ = "datos_avances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots_recibidos.id", ondelete="CASCADE"), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    etapa_nombre = Column(String(100), nullable=False)
    porcentaje_avance = Column(Numeric(5, 2), nullable=False)
    tareas_principales = Column(ARRAY(String), nullable=False)
    oficios_activos = Column(ARRAY(String), nullable=False)
    snapshot = relationship("SnapshotRecibido", back_populates="datos_avances")

class DatoSeguridad(Base):
    __tablename__ = "datos_seguridad"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots_recibidos.id", ondelete="CASCADE"), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    medidas_implementadas = Column(ARRAY(String), nullable=False)
    cobertura_art_declarada = Column(Boolean, nullable=False)
    snapshot = relationship("SnapshotRecibido", back_populates="datos_seguridad")

class DatoValidacion(Base):
    __tablename__ = "datos_validaciones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots_recibidos.id", ondelete="CASCADE"), nullable=False)
    fecha_validacion = Column(Date, nullable=False)
    estado_validacion = Column(String(50), nullable=False)
    responsable_tecnico = Column(String(200), nullable=False)
    snapshot = relationship("SnapshotRecibido", back_populates="datos_validaciones")
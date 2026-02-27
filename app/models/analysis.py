from sqlalchemy import Column, String, Date, DateTime, Integer, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db import Base
from app.models.enums import EstadoAnalisis

class Analisis(Base):
    __tablename__ = "analisis"
    __table_args__ = (
        Index('ix_analisis_proyecto_periodo', 'proyecto_codigo', 'periodo_desde', 'periodo_hasta'),
        Index('ix_analisis_estado', 'estado'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_codigo = Column(String(50), nullable=False, index=True)
    periodo_desde = Column(Date, nullable=False)
    periodo_hasta = Column(Date, nullable=False)
    
    fecha_solicitud = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_inicio_proceso = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)
    estado = Column(SQLEnum(EstadoAnalisis, native_enum=False), nullable=False, default=EstadoAnalisis.PENDIENTE)
    error_mensaje = Column(String(500), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    snapshot = relationship("SnapshotRecibido", back_populates="analisis", uselist=False, cascade="all, delete-orphan")
    invocaciones = relationship("InvocacionLLM", back_populates="analisis", cascade="all, delete-orphan")
    resultado = relationship("ResultadoAnalisis", back_populates="analisis", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analisis {self.proyecto_codigo} ({self.estado.value})>"
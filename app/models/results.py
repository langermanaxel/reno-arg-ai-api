from sqlalchemy import Column, String, DateTime, Integer, Numeric, Boolean, Text, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db import Base
from app.models.enums import CategoriaObservacion, NivelObservacion

class ResultadoAnalisis(Base):
    __tablename__ = "resultados_analisis"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, unique=True)
    resumen_general = Column(Text, nullable=False)
    estado_ejecucion = Column(Text, nullable=False)
    estado_planificacion = Column(Text, nullable=False)
    estado_seguridad = Column(Text, nullable=False)
    estado_validaciones = Column(Text, nullable=False)
    score_coherencia = Column(Numeric(5, 2), nullable=True)
    riesgos_identificados = Column(ARRAY(String), nullable=True)
    generado_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    analisis = relationship("Analisis", back_populates="resultado")
    observaciones = relationship("ObservacionGenerada", back_populates="resultado", cascade="all, delete-orphan", order_by="ObservacionGenerada.orden")

class ObservacionGenerada(Base):
    __tablename__ = "observaciones_generadas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resultado_id = Column(UUID(as_uuid=True), ForeignKey("resultados_analisis.id", ondelete="CASCADE"), nullable=False)
    categoria = Column(SQLEnum(CategoriaObservacion, native_enum=False), nullable=False)
    nivel = Column(SQLEnum(NivelObservacion, native_enum=False), nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    recomendacion = Column(Text, nullable=True)
    orden = Column(Integer, nullable=False)
    resultado = relationship("ResultadoAnalisis", back_populates="observaciones")
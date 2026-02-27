from sqlalchemy import Column, String, DateTime, Integer, Numeric, Boolean, Text, ForeignKey, Float, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db import Base

class InvocacionLLM(Base):
    __tablename__ = "invocaciones_llm"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False)
    modelo_usado = Column(String(100), nullable=False)
    tokens_prompt = Column(Integer, nullable=True)
    tokens_respuesta = Column(Integer, nullable=True)
    costo_estimado = Column(Numeric(10, 6), nullable=True)
    duracion_ms = Column(Integer, nullable=True)
    invocado_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    exitosa = Column(Boolean, nullable=False, default=False)
    error_detalle = Column(Text, nullable=True)

    analisis = relationship("Analisis", back_populates="invocaciones")
    prompt = relationship("PromptGenerado", back_populates="invocacion", uselist=False, cascade="all, delete-orphan")
    respuesta = relationship("RespuestaLLM", back_populates="invocacion", uselist=False, cascade="all, delete-orphan")

class PromptGenerado(Base):
    __tablename__ = "prompts_generados"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocacion_llm_id = Column(UUID(as_uuid=True), ForeignKey("invocaciones_llm.id", ondelete="CASCADE"), nullable=False, unique=True)
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    temperature = Column(Float, nullable=False, default=0.3)
    invocacion = relationship("InvocacionLLM", back_populates="prompt")

class RespuestaLLM(Base):
    __tablename__ = "respuestas_llm"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocacion_llm_id = Column(UUID(as_uuid=True), ForeignKey("invocaciones_llm.id", ondelete="CASCADE"), nullable=False, unique=True)
    respuesta_raw = Column(Text, nullable=False)
    respuesta_parseada = Column(Text, nullable=True)
    valida_estructuralmente = Column(Boolean, nullable=False, default=False)
    invocacion = relationship("InvocacionLLM", back_populates="respuesta")
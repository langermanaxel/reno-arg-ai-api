"""Auditoría completa de invocaciones LLM."""

from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, ForeignKey, Index, UUID
from sqlalchemy.orm import relationship

from app.models.core import Base, UUIDMixin, TimestampMixin
from app.models.analisis import Analisis

class InvocacionLLM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "invocacion_llm"
    
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"), index=True)
    modelo_usado = Column(String(100), nullable=False)
    tokens_prompt = Column(Integer)
    tokens_respuesta = Column(Integer)
    total_tokens = Column(Integer, index=True)
    duracion_ms = Column(Integer)
    exitosa = Column(Boolean, default=True, index=True)
    error_detalle = Column(Text)
    
    __table_args__ = (Index('ix_invocacion_modelo_exitosa', 'modelo_usado', 'exitosa'),)
    
    analisis = relationship("Analisis", back_populates="invocaciones")
    prompt_generado = relationship("PromptGenerado", uselist=False)
    respuesta_llm = relationship("RespuestaLLM", uselist=False)

class PromptGenerado(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "prompt_generado"
    
    invocacion_id = Column(UUID(as_uuid=True), ForeignKey("invocacion_llm.id"), index=True)
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    
    invocacion = relationship("InvocacionLLM", back_populates="prompt_generado")

class RespuestaLLM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "respuesta_llm"
    
    invocacion_id = Column(UUID(as_uuid=True), ForeignKey("invocacion_llm.id"), index=True)
    respuesta_raw = Column(Text, nullable=False)
    respuesta_parseada = Column(JSON)
    
    invocacion = relationship("InvocacionLLM", back_populates="respuesta_llm")

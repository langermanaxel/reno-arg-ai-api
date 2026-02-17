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
    invocaciones = relationship("InvocacionLLM", backref="analisis")

class SnapshotRecibido(Base):
    __tablename__ = "snapshot_recibido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    payload_completo = Column(Text) 
    recibido_at = Column(DateTime, default=datetime.utcnow)

    analisis = relationship("Analisis", back_populates="snapshot")
    proyecto = relationship("DatoProyecto", backref="snapshot")
    etapas = relationship("DatoEtapa", backref="snapshot")
    avances = relationship("DatoAvance", backref="snapshot")
    seguridad = relationship("DatoSeguridad", backref="snapshot")

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
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"))
    codigo = Column(String)
    nombre = Column(String)
    responsable_tecnico = Column(String)

class DatoEtapa(Base):
    __tablename__ = "dato_etapa"
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"))
    nombre = Column(String)
    estado = Column(String)
    avance_estimado = Column(Integer)

class DatoAvance(Base):
    __tablename__ = "dato_avance"
    id = Column(Integer, primary_key=True, index=True)
    # Por ahora lo vinculamos a Analisis para mantener consistencia con tu código actual
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"))
    
    fecha_registro = Column(Date, nullable=True)
    etapa_nombre = Column(String, nullable=True)
    porcentaje_avance = Column(Integer)
    presenta_desvios = Column(Boolean, default=False)
    supervisor = Column(String, nullable=True)
    
    # Guardamos las listas como JSON array para no crear 50 tablas pequeñas
    tareas_ejecutadas = Column(JSON) 
    oficios_activos = Column(JSON)

class DatoSeguridad(Base):
    __tablename__ = "dato_seguridad"
    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_recibido.id"))
    
    fecha_registro = Column(Date, nullable=True)
    
    # Aquí guardamos la lista completa de medidas [{"item": "Casco", "cumple": true}, ...]
    medidas_implementadas = Column(JSON)
    
    # Campos resumen útiles para queries rápidas
    total_medidas_chequeadas = Column(Integer, default=0)
    cumple_todas = Column(Boolean, default=False)

# --- TABLAS PARA PASO 3: AUDITORÍA LLM ---

class InvocacionLLM(Base):
    __tablename__ = "invocacion_llm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id"))
    modelo_usado = Column(String) # ej: "gpt-4o" o "llama-3"
    tokens_prompt = Column(Integer, nullable=True)
    tokens_respuesta = Column(Integer, nullable=True)
    duracion_ms = Column(Integer, nullable=True)
    exitosa = Column(Boolean, default=True)
    error_detalle = Column(Text, nullable=True)
    invocado_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    prompts = relationship("PromptGenerado", back_populates="invocacion", uselist=False)
    respuesta = relationship("RespuestaLLM", back_populates="invocacion", uselist=False)

class PromptGenerado(Base):
    __tablename__ = "prompt_generado"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocacion_id = Column(UUID(as_uuid=True), ForeignKey("invocacion_llm.id"))
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    generado_at = Column(DateTime, default=datetime.utcnow)

    invocacion = relationship("InvocacionLLM", back_populates="prompts")

class RespuestaLLM(Base):
    __tablename__ = "respuesta_llm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocacion_id = Column(UUID(as_uuid=True), ForeignKey("invocacion_llm.id"))
    respuesta_raw = Column(Text) # El JSON string tal cual vino de la IA
    respuesta_parseada = Column(JSON) # El objeto ya convertido
    recibida_at = Column(DateTime, default=datetime.utcnow)

    invocacion = relationship("InvocacionLLM", back_populates="respuesta")

# --- NUEVA TABLA: SEGURIDAD Y USUARIOS ---

class User(Base):
    __tablename__ = "usuarios"

    # Usamos UUID por consistencia con el resto de tu arquitectura
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # El hash de passlib
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
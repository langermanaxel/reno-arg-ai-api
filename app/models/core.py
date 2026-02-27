"""Modelos base y enums compartidos."""

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from app.db.base import Base
from pydantic import BaseModel, field_validator

# ========================================
# MIXINS REUTILIZABLES
# ========================================
class UUIDMixin:
    """UUID primary key estándar."""
    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class TimestampMixin:
    """Timestamps automáticos."""
    created_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       index=True)
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

# ========================================
# ENUMS COMPARTIDOS
# ========================================
class EstadoAnalisis(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"

class EstadoEtapa(str, enum.Enum):
    PLANIFICADA = "planificada"
    EN_EJECUCION = "en_ejecucion"
    FINALIZADA = "finalizada"
    PAUSADA = "pausada"

class NivelRiesgo(str, enum.Enum):
    INFORMATIVO = "informativo"
    ATENCION = "atencion"
    CRITICO = "critico"

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date
from typing import Optional
from .enums import EstadoAnalisis
from .results import ResultadoAnalisisOut

class AnalisisBase(BaseModel):
    proyecto_codigo: str = Field(..., min_length=3, max_length=50, example="CP-001")
    periodo_desde: date
    periodo_hasta: date

class AnalisisCreate(AnalisisBase):
    """Cuerpo de la petición para crear un nuevo análisis"""
    pass

class AnalisisOut(AnalisisBase):
    """Respuesta estándar de un análisis"""
    id: UUID
    estado: EstadoAnalisis
    fecha_solicitud: datetime
    error_mensaje: Optional[str] = None
    version: int
    
    # Opcional: incluir el resultado si el estado es COMPLETADO
    resultado: Optional[ResultadoAnalisisOut] = None

    class Config:
        from_attributes = True
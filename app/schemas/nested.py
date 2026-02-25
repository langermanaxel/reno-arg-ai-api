"""Schemas nested para datos estructurados."""

from pydantic import BaseModel, Field
from typing import List, Optional
from .enums import EstadoEtapa

class ProyectoData(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    responsable_tecnico: Optional[str] = Field(None, max_length=100)

class EtapaData(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    estado: EstadoEtapa
    avance_estimado: float = Field(0.0, ge=0.0, le=100.0)

class AvanceData(BaseModel):
    fecha: Optional[str] = Field(None)
    supervisor: Optional[str] = Field(None, max_length=100)
    porcentaje_avance: float = Field(0.0, ge=0.0, le=100.0)
    presenta_desvios: bool = False
    tareas_ejecutadas: List[str] = []
    oficios_activos: List[str] = []

class MedidaSeguridad(BaseModel):
    cumple: bool
    descripcion: Optional[str] = None

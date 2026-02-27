from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional, Any

class DatoProyectoBase(BaseModel):
    proyecto_nombre: str = Field(..., example="Edificio RENO I")
    ubicacion: str
    tipo_intervencion: str
    superficie_m2: float = Field(..., gt=0)
    sistema_constructivo: str
    responsable_tecnico_nombre: str
    fecha_inicio: date

class DatoEtapaBase(BaseModel):
    etapa_nombre: str
    etapa_orden: int
    fecha_inicio_estimada: Optional[date] = None
    fecha_fin_estimada: Optional[date] = None
    estado: str

class DatoAvanceBase(BaseModel):
    fecha_registro: date
    etapa_nombre: str
    porcentaje_avance: float = Field(..., ge=0, le=100)
    tareas_principales: List[str]
    oficios_activos: List[str]

class SnapshotInput(BaseModel):
    """Esquema de entrada para el snapshot completo"""
    proyecto: DatoProyectoBase
    etapas: List[DatoEtapaBase]
    avances: List[DatoAvanceBase]
    seguridad_higiene: List[Any]  # Se puede detallar más según necesidad
    validaciones_tecnicas: List[Any]

    class Config:
        from_attributes = True
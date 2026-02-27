from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any
from .enums import CategoriaObservacion, NivelObservacion

class ObservacionOut(BaseModel):
    id: Optional[Any] = None # UUID en el futuro
    categoria: CategoriaObservacion
    nivel: NivelObservacion
    titulo: str = Field(..., max_length=200)
    descripcion: str
    recomendacion: Optional[str] = None
    orden: int

    class Config:
        from_attributes = True

class ResultadoAnalisisOut(BaseModel):
    resumen_general: str
    estado_ejecucion: str
    estado_planificacion: str
    estado_seguridad: str
    estado_validaciones: str
    score_coherencia: Optional[float] = Field(None, ge=0, le=100)
    riesgos_identificados: List[str] = []
    observaciones: List[ObservacionOut]
    generado_at: datetime

    class Config:
        from_attributes = True
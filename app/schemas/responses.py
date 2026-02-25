"""Schemas de respuesta para endpoints."""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class AnalisisResultado(BaseModel):
    """Resultado del análisis IA."""
    analisis_id: str
    estado: str
    resumen_general: Optional[str] = None
    score_coherencia: Optional[float] = None
    detecta_riesgos: bool = False
    riesgos: List[Dict[str, Any]] = []

class SnapshotResponse(BaseModel):
    """Respuesta completa del análisis."""
    id: str
    estado: str
    datos_obra: Dict[str, Any]
    auditoria_ia: List[Dict[str, Any]]
    resultado_negocio: AnalisisResultado

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "uuid-123",
                "estado": "COMPLETADO",
                "datos_obra": {"proyecto": "Hospital Santa Cruz"},
                "resultado_negocio": {
                    "analisis_id": "uuid-123",
                    "estado": "COMPLETADO",
                    "detecta_riesgos": False
                }
            }
        }
    }

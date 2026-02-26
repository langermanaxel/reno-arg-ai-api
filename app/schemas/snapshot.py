"""Schema principal SnapshotCreate + validadores."""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any
import re
from .nested import ProyectoData  # Opcional para docs

class SnapshotCreate(BaseModel):
    """Snapshot de proyecto para análisis IA."""
    
    proyecto_codigo: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Código único del proyecto",
        example="PROY-2026-001"
    )
    
    datos: Dict[str, Any] = Field(
        ...,
        description="Datos estructurados del proyecto"
    )

    @field_validator('proyecto_codigo')
    @classmethod
    def validate_proyecto_codigo(cls, v: str) -> str:
        if not re.match(r'^[A-Z0-9_-]+$', v):
            raise ValueError('Solo letras mayúsculas, números, guiones y guiones bajos')
        return v.upper()

    @field_validator('datos')
    @classmethod
    def validate_datos_estructura(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estructura mínima esperada."""
        required_fields = ["proyecto"]
        
        for field in required_fields:
            if field not in v:
                raise ValueError(f"'{field}' es obligatorio en datos")
        
        proyecto = v.get("proyecto", {})
        if not isinstance(proyecto, dict) or not proyecto.get("codigo"):
            raise ValueError("'proyecto.codigo' es obligatorio")
        
        return v

    @field_validator('datos')
    @classmethod
    def validate_datos_coherencia(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Valida límites de datos."""
        etapas = v.get("etapas", [])
        avances = v.get("registros_avance", [])
        
        if len(etapas) > 100:
            raise ValueError("Máximo 100 etapas permitidas")
        if len(avances) > 500:
            raise ValueError("Máximo 500 registros de avance")
        
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "proyecto_codigo": "PROY-2026-001",
                "datos": {
                    "proyecto": {"codigo": "PROY-2026-001", "nombre": "Hospital Santa Cruz"},
                    "etapas": [{"nombre": "Cimientos", "estado": "en_ejecucion", "avance_estimado": 85.5}]
                }
            }]
        },
        "validate_assignment": True,
        "arbitrary_types_allowed": True
    }

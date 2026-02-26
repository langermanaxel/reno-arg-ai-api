"""Schema principal SnapshotCreate + validadores."""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Any, Optional
import re


class SnapshotCreate(BaseModel):
    """Snapshot de proyecto para análisis IA."""

    proyecto_codigo: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Código único del proyecto",
        example="RENO-AR-2026-014",
    )

    datos: Dict[str, Any] = Field(
        ...,
        description="Datos estructurados del proyecto",
    )

    # --- Campos LLM configurables por request ---
    model: Optional[str] = Field(
        default=None,
        description="Modelo LLM a usar. Si no se especifica, usa el fallback configurado.",
        example="openai/gpt-4o-mini",
    )

    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Temperatura del modelo. Default 0.3 para respuestas consistentes.",
    )

    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt personalizado. Si no se especifica, usa el default del PromptBuilder.",
    )

    instrucciones_extra: Optional[str] = Field(
        default=None,
        description="Instrucciones adicionales que se agregan al user prompt.",
    )

    @field_validator("proyecto_codigo")
    @classmethod
    def validate_proyecto_codigo(cls, v: str) -> str:
        # Normalizamos primero, validamos después
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9_-]+$", v):
            raise ValueError("Solo letras, números, guiones y guiones bajos")
        return v

    @field_validator("datos")
    @classmethod
    def validate_datos_estructura(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if "proyecto" not in v:
            raise ValueError("'proyecto' es obligatorio en datos")
        proyecto = v.get("proyecto", {})
        if not isinstance(proyecto, dict) or not proyecto.get("codigo"):
            raise ValueError("'proyecto.codigo' es obligatorio")
        return v

    @field_validator("datos")
    @classmethod
    def validate_datos_coherencia(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if len(v.get("etapas", [])) > 100:
            raise ValueError("Máximo 100 etapas permitidas")
        if len(v.get("registros_avance", [])) > 500:
            raise ValueError("Máximo 500 registros de avance")
        return v

    @model_validator(mode="after")
    def sincronizar_proyecto_codigo(self) -> "SnapshotCreate":
        """Garantiza que proyecto_codigo y datos.proyecto.codigo sean iguales."""
        codigo_datos = self.datos.get("proyecto", {}).get("codigo", "").upper()
        if codigo_datos and codigo_datos != self.proyecto_codigo:
            raise ValueError(
                f"proyecto_codigo '{self.proyecto_codigo}' no coincide "
                f"con datos.proyecto.codigo '{codigo_datos}'"
            )
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "proyecto_codigo": "RENO-AR-2026-014",
                    "model": "openai/gpt-4o-mini",
                    "temperature": 0.3,
                    "system_prompt": None,
                    "instrucciones_extra": None,
                    "datos": {
                        "proyecto": {
                            "codigo": "RENO-AR-2026-014",
                            "nombre": "Reforma vivienda unifamiliar Barrio Caballito",
                        },
                        "etapas": [
                            {
                                "nombre": "Obra gruesa",
                                "estado": "EN_CURSO",
                                "avance_estimado": 45,
                            }
                        ],
                    },
                }
            ]
        },
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }
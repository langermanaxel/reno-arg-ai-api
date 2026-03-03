"""Schema principal SnapshotCreate + validadores."""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List
from datetime import date
from enum import Enum
import re

class EstadoEtapa(str, Enum):
    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"
    PENDIENTE = "PENDIENTE"


class Project(BaseModel):
    codigo: str = Field(..., min_length=5)
    nombre: str
    responsable_tecnico: str


class Periodo(BaseModel):
    desde: date
    hasta: date

    @model_validator(mode="after")
    def validar_rango_fechas(self):
        if self.hasta < self.desde:
            raise ValueError("La fecha 'hasta' no puede ser anterior a 'desde'")
        return self


class Etapa(BaseModel):
    nombre: str
    estado: EstadoEtapa
    avance_estimado: int = Field(ge=0, le=100)


class RegistroAvance(BaseModel):
    fecha: date
    supervisor: str
    tareas_ejecutadas: List[str]
    oficios_activos: List[str]
    porcentaje_avance: int = Field(ge=0, le=100)


class CoberturaART(BaseModel):
    entidad: str
    vigencia: str


class MedidasSeguridad(BaseModel):
    fecha: date
    implementadas: List[str]
    cobertura_art: CoberturaART


class ValidacionTecnica(BaseModel):
    fecha: date
    estado: EstadoEtapa
    etapa: str
    responsable: str


class SnapshotCreate(BaseModel):
    """Snapshot de proyecto para análisis IA."""

    project: Project
    periodo: Periodo
    etapas: Etapa
    registros_avance: RegistroAvance
    medidas_seguridad: MedidasSeguridad
    validaciones_tecnicas: ValidacionTecnica

    @field_validator("project")
    @classmethod
    def validar_codigo_proyecto(cls, value):
        patron = r"^[A-Z]+-[A-Z]{2}-\d{4}-\d{3}$"
        if not re.match(patron, value.codigo):
            raise ValueError("Formato de código de proyecto inválido")
        return value
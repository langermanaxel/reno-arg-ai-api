"""Enums compartidos para schemas."""

from enum import Enum

class EstadoEtapa(str, Enum):
    PLANIFICADA = "planificada"
    EN_EJECUCION = "en_ejecucion"
    FINALIZADA = "finalizada"
    PAUSADA = "pausada"

class NivelRiesgo(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

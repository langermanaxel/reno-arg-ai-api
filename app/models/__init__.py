from app.db import Base, engine
# Importar todos los modelos para que Base.metadata los registre
from .enums import EstadoAnalisis, CategoriaObservacion, NivelObservacion
from .analysis import Analisis
from .snapshot import (
    SnapshotRecibido, DatoProyecto, DatoEtapa, 
    DatoAvance, DatoSeguridad, DatoValidacion
)
from .ai_process import InvocacionLLM, PromptGenerado, RespuestaLLM
from .results import ResultadoAnalisis, ObservacionGenerada

# Helpers para inicialización
def init_db(engine):
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada: Tablas creadas.")

def drop_all(engine):
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Base de datos reseteada: Tablas eliminadas.")

# Exportar todo lo que necesites usar externamente
__all__ = [
    "Base",
    "Analisis",
    "SnapshotRecibido",
    "DatoProyecto",
    "DatoEtapa",
    "DatoAvance",
    "DatoSeguridad",
    "DatoValidacion",
    "InvocacionLLM",
    "PromptGenerado",
    "RespuestaLLM",
    "ResultadoAnalisis",
    "ObservacionGenerada",
    "EstadoAnalisis",
    "CategoriaObservacion",
    "NivelObservacion",
    "init_db",
    "drop_all"
]
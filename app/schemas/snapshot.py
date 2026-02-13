from pydantic import BaseModel
from typing import List, Dict, Any

class SnapshotCreate(BaseModel):
    proyecto_codigo: str
    datos: Dict[str, Any] # Aquí recibiremos todo el JSON complejo
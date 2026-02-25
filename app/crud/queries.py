"""Queries optimizadas para lecturas."""

from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any
from app.models import Analisis, SnapshotRecibido, ResultadoAnalisis

def get_analisis_completo(db: Session, analisis_id: str) -> Dict[str, Any]:
    """Obtiene análisis completo optimizado."""
    analisis = db.query(Analisis).options(
        joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.proyecto),
        joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.etapas),
        joinedload(Analisis.resultado).joinedload(ResultadoAnalisis.observaciones),
        joinedload(Analisis.invocaciones)
    ).filter(Analisis.id == analisis_id).first()
    
    if not analisis:
        return None
    
    return {
        "id": analisis.id,
        "estado": analisis.estado,
        "datos_obra": {
            "proyecto": getattr(analisis.snapshot, 'proyecto', None),
            "etapas_registradas": len(getattr(analisis.snapshot, 'etapas', []))
        },
        "auditoria_ia": [{"modelo": i.modelo_usado, "exitoso": i.exitosa} 
                        for i in getattr(analisis, 'invocaciones', [])],
        "resultado_negocio": getattr(analisis, 'resultado', None)
    }

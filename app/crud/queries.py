"""Queries optimizadas para lecturas."""

from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional
from app.models import Analisis, SnapshotRecibido, ResultadoAnalisis


def get_analisis_completo(db: Session, analisis_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene análisis completo con todos sus datos relacionados."""
    analisis = (
        db.query(Analisis)
        .options(
            joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.proyecto),
            joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.etapas),
            joinedload(Analisis.resultado).joinedload(ResultadoAnalisis.observaciones),
            joinedload(Analisis.invocaciones),
        )
        .filter(Analisis.id == analisis_id)
        .first()
    )

    if not analisis:
        return None

    # --- Snapshot / datos de obra ---
    snapshot = getattr(analisis, "snapshot", None)
    proyecto = getattr(snapshot, "proyecto", None) if snapshot else None
    etapas = getattr(snapshot, "etapas", []) if snapshot else []

    datos_obra = {
        "proyecto": {
            "codigo": getattr(proyecto, "codigo", None),
            "nombre": getattr(proyecto, "nombre", None),
            "responsable_tecnico": getattr(proyecto, "responsable_tecnico", None),
        } if proyecto else None,
        "etapas_registradas": len(etapas),
        "etapas": [
            {
                "nombre": getattr(e, "nombre", None),
                "estado": getattr(e, "estado", None),
                "avance_estimado": getattr(e, "avance_estimado", None),
            }
            for e in etapas
        ],
        # Payload completo como fallback si no hay tablas normalizadas
        "payload_completo": getattr(snapshot, "payload_completo", None) if snapshot else None,
    }

    # --- Auditoría IA ---
    invocaciones = getattr(analisis, "invocaciones", []) or []
    auditoria_ia = [
        {
            "modelo": i.modelo_usado,
            "exitoso": i.exitosa,
            "error": i.error_detalle,
            "tokens_prompt": i.tokens_prompt,
            "tokens_respuesta": i.tokens_respuesta,
            "total_tokens": i.total_tokens,
            "duracion_ms": i.duracion_ms,
            "costo_usd": getattr(i, "costo_usd", None),
        }
        for i in invocaciones
    ]

    # --- Resultado de negocio ---
    resultado = getattr(analisis, "resultado", None)
    observaciones = getattr(resultado, "observaciones", []) if resultado else []

    resultado_negocio = {
        "resumen_general": getattr(resultado, "resumen_general", None),
        "score_coherencia": getattr(resultado, "score_coherencia", None),
        "detecta_riesgos": getattr(resultado, "detecta_riesgos", False),
        "observaciones": [
            {
                "titulo": getattr(o, "titulo", None),
                "descripcion": getattr(o, "descripcion", None),
                "nivel": getattr(o, "nivel", None),
            }
            for o in observaciones
        ],
    } if resultado else None

    return {
        "id": str(analisis.id),
        "estado": analisis.estado,
        "proyecto_codigo": analisis.proyecto_codigo,
        "created_at": analisis.created_at,
        "datos_obra": datos_obra,
        "auditoria_ia": auditoria_ia,
        "resultado_negocio": resultado_negocio,
    }
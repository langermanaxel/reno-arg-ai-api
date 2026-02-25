from typing import Dict, Any, List
from app.models.analisis import (
    DatoProyecto, DatoEtapa, DatoAvance, DatoSeguridad
)
from app.utils.helpers import normalize_item, parse_fecha
from datetime import datetime, timezone

class DatosMapper:
    @staticmethod
    def map_proyecto(snapshot_id: int, datos: Dict[str, Any]) -> DatoProyecto:
        proy = datos.get("proyecto", {})
        return DatoProyecto(
            snapshot_id=snapshot_id,
            codigo=proy.get("codigo"),
            nombre=proy.get("nombre"),
            responsable_tecnico=proy.get("responsable_tecnico")
        )

    @staticmethod
    def map_etapas(snapshot_id: int, etapas: List[Any]) -> List[DatoEtapa]:
        return [
            DatoEtapa(
                snapshot_id=snapshot_id,
                nombre=e.get("nombre"),
                estado=e.get("estado"),
                avance_estimado=e.get("avance_estimado", 0)
            )
            for e in [normalize_item(etapa) for etapa in etapas]
        ]

    @staticmethod
    def map_avances(snapshot_id: int, avances: List[Any]) -> List[DatoAvance]:
        return [
            DatoAvance(
                snapshot_id=snapshot_id,
                fecha_registro=parse_fecha(a.get("fecha")),
                supervisor=a.get("supervisor"),
                porcentaje_avance=a.get("porcentaje_avance", 0),
                presenta_desvios=a.get("presenta_desvios", False),
                tareas_ejecutadas=a.get("tareas_ejecutadas", []),
                oficios_activos=a.get("oficios_activos", [])
            )
            for a in [normalize_item(avance) for avance in avances]
        ]

    @staticmethod
    def map_seguridad(snapshot_id: int, medidas: List[Any]) -> DatoSeguridad:
        if not medidas:
            return None
        normalizadas = [normalize_item(m) for m in medidas]
        total = len(normalizadas)
        cumple = sum(1 for m in normalizadas if m.get("cumple") is True)
        return DatoSeguridad(
            snapshot_id=snapshot_id,
            fecha_registro=datetime.now(timezone.utc).date(),
            medidas_implementadas=medidas,
            total_medidas_chequeadas=total,
            cumple_todas=(total == cumple)
        )

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.models.operaciones import DatoEtapa, DatoAvance, DatoSeguridad
from app.models.datos import DatoProyecto
from app.utils.helpers import normalize_item, parse_fecha


class DatosMapper:

    @staticmethod
    def map_proyecto(snapshot_id: Any, datos: Dict[str, Any]) -> Optional[DatoProyecto]:
        proy = datos.get("proyecto")

        # Si no hay proyecto o no tiene código, no persistir
        if not proy or not isinstance(proy, dict) or not proy.get("codigo"):
            return None

        return DatoProyecto(
            snapshot_id=snapshot_id,
            codigo=proy.get("codigo"),
            nombre=proy.get("nombre"),
            responsable_tecnico=proy.get("responsable_tecnico"),
        )

    @staticmethod
    def map_etapas(snapshot_id: Any, etapas: List[Any]) -> List[DatoEtapa]:
        resultado = []
        for etapa in etapas:
            e = normalize_item(etapa)
            if not e or not isinstance(e, dict):
                continue
            resultado.append(
                DatoEtapa(
                    snapshot_id=snapshot_id,
                    nombre=e.get("nombre"),
                    estado=e.get("estado"),
                    avance_estimado=e.get("avance_estimado", 0),
                )
            )
        return resultado

    @staticmethod
    def map_avances(snapshot_id: Any, avances: List[Any]) -> List[DatoAvance]:
        resultado = []
        for avance in avances:
            a = normalize_item(avance)
            if not a or not isinstance(a, dict):
                continue
            resultado.append(
                DatoAvance(
                    snapshot_id=snapshot_id,
                    fecha_registro=parse_fecha(a.get("fecha")),
                    supervisor=a.get("supervisor"),
                    porcentaje_avance=a.get("porcentaje_avance", 0),
                    presenta_desvios=a.get("presenta_desvios", False),
                    tareas_ejecutadas=a.get("tareas_ejecutadas", []),
                    oficios_activos=a.get("oficios_activos", []),
                )
            )
        return resultado

    @staticmethod
    def map_seguridad(snapshot_id: Any, medidas: List[Any]) -> Optional[DatoSeguridad]:
        if not medidas:
            return None

        normalizadas = [normalize_item(m) for m in medidas if normalize_item(m)]
        if not normalizadas:
            return None

        total = len(normalizadas)
        cumple = sum(1 for m in normalizadas if isinstance(m, dict) and m.get("cumple") is True)

        return DatoSeguridad(
            snapshot_id=snapshot_id,
            fecha_registro=datetime.now(timezone.utc).date(),
            medidas_implementadas=medidas,
            total_medidas_chequeadas=total,
            cumple_todas=(total == cumple),
        )
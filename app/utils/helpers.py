import re
import json
from datetime import datetime, timezone
from typing import Dict, Any

FECHA_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]

def normalize_item(item: Any) -> Dict[str, Any]:
    """Normaliza dict/objeto → dict."""
    if isinstance(item, dict):
        return item
    if hasattr(item, '__dict__'):
        return item.__dict__
    return dict(item)

def parse_fecha(fecha_str: str) -> datetime.date:
    """Parse múltiples formatos de fecha."""
    if not fecha_str:
        return datetime.now(timezone.utc).date()
    for fmt in FECHA_FORMATS:
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue
    return datetime.now(timezone.utc).date()

def parse_json_seguro(contenido: str) -> Dict[str, Any]:
    """JSON parsing robusto con regex fallback."""
    try:
        return json.loads(contenido)
    except json.JSONDecodeError:
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', contenido)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return {}

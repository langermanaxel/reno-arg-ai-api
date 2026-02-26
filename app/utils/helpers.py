import re
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

FECHA_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"]

def normalize_item(item: Any) -> Dict[str, Any]:
    """Normaliza dict/objeto → dict."""
    if isinstance(item, dict):
        return item
    if hasattr(item, '__dict__'):
        return item.__dict__
    try:
        return dict(item)
    except (TypeError, ValueError):
        return {}

def parse_fecha(fecha_str: str) -> datetime.date:
    """Parse múltiples formatos de fecha con fallback seguro."""
    if not fecha_str or not isinstance(fecha_str, str):
        return datetime.now(timezone.utc).date()
    for fmt in FECHA_FORMATS:
        try:
            return datetime.strptime(fecha_str.strip(), fmt).date()
        except ValueError:
            continue
    return datetime.now(timezone.utc).date()

def parse_json_seguro(contenido: str) -> Dict[str, Any]:
    """
    JSON parsing robusto. 
    Limpia bloques de Markdown y usa un regex más simple para extraer el objeto principal.
    """
    if not contenido:
        return {}

    # 1. Limpieza básica: quitar espacios extremos
    contenido = contenido.strip()

    # 2. Intento 1: Parseo directo
    try:
        return json.loads(contenido)
    except json.JSONDecodeError:
        pass

    # 3. Intento 2: Buscar bloques de código Markdown ```json ... ```
    # Los LLMs aman envolver el JSON en estos bloques.
    match_markdown = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", contenido, re.DOTALL)
    if match_markdown:
        try:
            return json.loads(match_markdown.group(1))
        except json.JSONDecodeError:
            pass

    # 4. Intento 3: Extraer lo que parezca un objeto JSON { ... }
    # Buscamos desde la primera '{' hasta la última '}'
    try:
        start = contenido.find('{')
        end = contenido.rfind('}')
        if start != -1 and end != -1:
            return json.loads(contenido[start:end+1])
    except json.JSONDecodeError as e:
        logger.error(f"Error definitivo parseando JSON: {e}")
    
    return {}
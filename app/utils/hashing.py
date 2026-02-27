import hashlib
import json
from typing import Any

def generar_hash_payload(payload: dict[str, Any]) -> int:
    """
    Genera un hash numérico a partir del payload JSON para detectar 
    snapshots duplicados en la base de datos.
    """
    payload_str = json.dumps(payload, sort_keys=True).encode('utf-8')
    # Usamos MD5 y lo convertimos a un entero (limitado a 32 bits para DB)
    return int(hashlib.md5(payload_str).hexdigest()[:8], 16)
import httpx
import json
import os
import logging
from app.db import engine
from app.models import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync_models")

# Modelos que no funcionan correctamente: aliases, de pago, o con respuestas vacías
MODELOS_EXCLUIDOS = {
    "openrouter/free",          # alias, devuelve respuestas vacías
    "openrouter/auto",          # alias no determinístico
    "openrouter/bodybuilder",   # alias interno
    "liquid/lfm-2-24b-a2b",    # requiere pago (402)
    "liquid/lfm2-8b-a1b",      # requiere pago
    "liquid/lfm-2.2-6b",       # requiere pago
}

def sync_db_schema():
    """Asegura que las tablas existan antes de que la app arranque"""
    try:
        logger.info("🗄️  Sincronizando esquema de base de datos...")
        init_db(engine)
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")

def sync_openrouter_models():
    """Consulta OpenRouter y genera el registro de modelos"""
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY', '')}",
        "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api",
    }

    favoritos = [
        "google/gemma-3-27b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
    ]

    try:
        logger.info("🔍 Consultando modelos en OpenRouter...")
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json().get('data', [])

        # Filtro: gratuitos o de bajo costo, excluyendo los problemáticos
        models_list = [
            m['id'] for m in data
            if (
                float(m.get('pricing', {}).get('prompt', 0)) < 0.0000001
                or ":free" in m['id']
            )
            and m['id'] not in MODELOS_EXCLUIDOS
        ]

        final_list = favoritos + [
            m for m in models_list
            if m not in favoritos and m not in MODELOS_EXCLUIDOS
        ]

    except Exception as e:
        logger.error(f"❌ Falló el fetch de modelos: {e}. Usando fallback.")
        final_list = [m for m in favoritos if m not in MODELOS_EXCLUIDOS]

    # Persistencia del registro
    os.makedirs("app/config", exist_ok=True)
    with open("app/config/models_registry.py", "w", encoding="utf-8") as f:
        f.write("# Archivo generado automáticamente por sync_models.py\n")
        f.write(f"AVAILABLE_MODELS = {json.dumps(final_list, indent=4)}\n")

    logger.info(f"✅ Registro actualizado con {len(final_list)} modelos.")

if __name__ == "__main__":
    # 1. Primero la DB (Crítico para que el contenedor sea funcional)
    sync_db_schema()
    # 2. Luego los modelos de IA
    sync_openrouter_models()
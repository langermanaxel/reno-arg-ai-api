import httpx  # <--- Cambiado de requests a httpx
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync_models")

def sync_openrouter_models():
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY', '')}",
        "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api", 
    }

    try:
        logger.info("🔍 Consultando modelos disponibles en OpenRouter...")
        # Usamos el cliente síncrono de httpx para que sea simple
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json().get('data', [])

        # Filtro de bajo costo o gratuitos
        models_list = [
            m['id'] for m in data 
            if float(m.get('pricing', {}).get('prompt', 0)) < 0.0000001 or ":free" in m['id']
        ]
        
        favoritos = [
            "google/gemma-3-27b-it:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-small-3.1-24b-instruct:free"
        ]
        
        final_list = favoritos + [m for m in models_list if m not in favoritos]

    except Exception as e:
        logger.error(f"❌ Falló sync: {e}")
        # Mantenemos los favoritos como fallback si falla la red
        final_list = ["google/gemma-3-27b-it:free", "meta-llama/llama-3.3-70b-instruct:free"]

    os.makedirs("app/config", exist_ok=True)
    with open("app/config/models_registry.py", "w") as f:
        f.write(f"AVAILABLE_MODELS = {json.dumps(final_list, indent=4)}\n")
    
    logger.info(f"✅ Registro actualizado con {len(final_list)} modelos.")

if __name__ == "__main__":
    sync_openrouter_models()
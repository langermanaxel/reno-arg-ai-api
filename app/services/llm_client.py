import httpx
import asyncio
import json
from app.core.settings import settings
from app.core.logging import get_logger

try:
    from app.config.models_registry import AVAILABLE_MODELS
except ImportError:
    AVAILABLE_MODELS = ["google/gemma-3-27b-it:free", "openrouter/free"]

logger = get_logger("app.llm_client")

class LLMClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.modelos_fallback = AVAILABLE_MODELS[:5] 
        logger.info(f"🚀 LLMClient iniciado con {len(self.modelos_fallback)} modelos.")

    async def enviar_prompt(self, system_prompt: str, user_prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api",
            "X-Title": settings.PROJECT_NAME,
            "Content-Type": "application/json"
        }

        intentos_fallidos = []

        # ✅ Usamos un solo cliente para todos los reintentos
        async with httpx.AsyncClient(timeout=60.0) as client:
            for i, modelo in enumerate(self.modelos_fallback):
                logger.debug(f"🤖 Intento {i+1}: Probando {modelo}")
                
                payload = {
                    "model": modelo,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }

                try:
                    response = await client.post(self.url, headers=headers, json=payload)
                    
                    # Manejo de Rate Limit (429)
                    if response.status_code == 429:
                        wait_time = (i + 1) * 2 # Incrementa: 2s, 4s, 6s...
                        logger.warning(f"⏳ Rate limit en {modelo}. Reintentando en {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue

                    datos = response.json()

                    if response.status_code == 200 and "error" not in datos:
                        logger.info(f"✅ ÉXITO con modelo: {modelo}")
                        return datos
                    
                    # Error lógico de la API (ej: modelo sobrecargado)
                    error_info = datos.get("error", {})
                    msg_error = error_info.get("message", "Error desconocido")
                    logger.warning(f"❌ FALLÓ {modelo}: {msg_error}")
                    intentos_fallidos.append(f"{modelo}: {msg_error}")

                    # Pequeña espera antes de saltar al siguiente modelo
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"⚠️ Excepción de red con {modelo}: {str(e)}")
                    intentos_fallidos.append(f"{modelo}: Error de red")
                    await asyncio.sleep(1)

        logger.error(f"🚨 FALLO TOTAL. Resumen: {intentos_fallidos}")
        return {
            "error": {
                "message": "Fallo total en cascada de modelos.",
                "details": intentos_fallidos
            }
        }
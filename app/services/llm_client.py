import httpx
import asyncio
import json
from app.core.settings import settings
from app.core.logging import get_logger
# --- IMPORTAMOS LA LISTA SINCRONIZADA ---
try:
    from app.config.models_registry import AVAILABLE_MODELS
except ImportError:
    # Fallback por si el archivo aún no se genera
    AVAILABLE_MODELS = ["google/gemma-3-27b-it:free", "openrouter/free"]

logger = get_logger("app.settings")

class LLMClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        # Usamos los primeros 5 modelos de la lista sincronizada para no hacer bucles infinitos
        self.modelos_fallback = AVAILABLE_MODELS[:5] 
        logger.info(f"🚀 LLMClient iniciado con {len(self.modelos_fallback)} modelos de fallback.")

    async def enviar_prompt(self, system_prompt: str, user_prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api",
            "X-Title": settings.PROJECT_NAME,
            "Content-Type": "application/json"
        }

        intentos_fallidos = []

        for modelo in self.modelos_fallback:
            logger.debug(f"Intentando con modelo: {modelo}...")
            
            payload = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }

            try:
                print(payload)
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.url, 
                        headers=headers, 
                        json=payload, 
                        timeout=45.0
                    )
                    
                    datos = response.json()

                    if response.status_code == 200 and "error" not in datos:
                        logger.info(f"✅ ÉXITO con modelo: {modelo}")
                        return datos
                    
                    msg_error = datos.get("error", {}).get("message", "Sin mensaje de error")
                    logger.warning(f"❌ FALLÓ {modelo}: {msg_error}")
                    intentos_fallidos.append(f"{modelo}: {msg_error}")
                    
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"⚠️ Excepción de red con {modelo}: {str(e)}")
                intentos_fallidos.append(f"{modelo}: Error de red")
                continue

        logger.error(f"🚨 TODOS LOS MODELOS FALLARON. Resumen: {intentos_fallidos}")
        return {
            "error": {
                "message": "Fallo total en cascada de modelos.",
                "details": intentos_fallidos
            }
        }
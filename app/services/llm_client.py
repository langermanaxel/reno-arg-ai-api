import httpx
import asyncio
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
        logger.info(f"🚀 LLMClient iniciado con {len(self.modelos_fallback)} modelos de fallback.")
    async def enviar_prompt(
        self,
        messages: list,
        modelo: str | None = None,
        temperature: float = 0.3,
    ):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Title": settings.PROJECT_NAME,
            "Content-Type": "application/json",
        }

        # Construcción segura de lista de modelos
        if modelo:
            modelos_a_intentar = [modelo] + self.modelos_fallback
        else:
            modelos_a_intentar = self.modelos_fallback

        intentos_fallidos = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            for i, m in enumerate(modelos_a_intentar):

                logger.debug(f"🤖 Intento {i+1}: Probando modelo '{m}'")
                logger.debug(f"🤖 Messages: {messages}")

                payload = {
                    "model": m,
                    "temperature": temperature,
                    "messages": messages,
                }

                try:
                    response = await client.post(
                        self.url,
                        headers=headers,
                        json=payload,   # ✅ Enviar payload completo
                    )

                    # Manejo rate limit
                    if response.status_code == 429:
                        wait_time = (i + 1) * 2
                        logger.warning(
                            f"⏳ Rate limit en '{m}'. Reintentando en {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    datos = response.json()

                    # Validación básica de respuesta OpenAI-style
                    if "error" not in datos:
                        logger.info(f"✅ ÉXITO con modelo: '{m}'")
                        return datos

                    # Error lógico devuelto por API
                    error_info = datos.get("error", {})
                    msg_error = error_info.get("message", "Error desconocido")

                    logger.warning(f"❌ FALLÓ '{m}': {msg_error}")
                    intentos_fallidos.append(f"{m}: {msg_error}")

                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"⚠️ Excepción con '{m}': {str(e)}")
                    intentos_fallidos.append(f"{m}: {str(e)}")
                    await asyncio.sleep(1)

        logger.error(f"🚨 FALLO TOTAL. Resumen: {intentos_fallidos}")

        return {
            "error": {
                "message": "Fallo total en cascada de modelos.",
                "details": intentos_fallidos,
            }
        }
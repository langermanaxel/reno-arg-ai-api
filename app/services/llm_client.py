import httpx
import asyncio
from app.core.config import settings  # Importación centralizada
from app.utils.logger import logger

class LLMClient:
    def __init__(self):
        # Pydantic Settings ya limpió y validó esta key
        self.api_key = settings.OPENROUTER_API_KEY
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Log de confirmación usando settings
        logger.info(f"🚀 LLMClient iniciado con modelo prioritario: google/gemini-2.0-flash-lite...")

        self.modelos_fallback = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "openrouter/free",
            "stepfun/step-3.5-flash:free",
            "upstage/solar-pro-3:free",
            "arcee-ai/trinity-large-preview:free"
        ]

    async def enviar_prompt(self, system_prompt: str, user_prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api",
            "X-Title": settings.PROJECT_NAME,  # Usamos el nombre desde config
            "Content-Type": "application/json"
        }

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
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.url, 
                        headers=headers, 
                        json=payload, 
                        timeout=30.0
                    )
                    
                    datos = response.json()

                    if response.status_code == 200 and "error" not in datos:
                        logger.info(f"✅ ÉXITO con modelo: {modelo}")
                        return datos
                    
                    error_info = datos.get("error", {}).get("message", "Error desconocido")
                    logger.warning(f"❌ FALLÓ {modelo}: {error_info}")
                    
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"⚠️ Error de conexión con {modelo}: {str(e)}")
                continue

        return {"error": {"message": "Ningún modelo de la lista de fallback respondió correctamente."}}
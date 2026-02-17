import httpx
import os
import asyncio
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class LLMClient:
    def __init__(self):
        # Cargamos la key y limpiamos espacios o comillas accidentales
        raw_key = os.getenv("OPENROUTER_API_KEY", "")
        self.api_key = raw_key.replace('"', '').replace("'", "").strip()
    
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
        if not self.api_key:
            logger.error("❌ CRÍTICO: No se detectó OPENROUTER_API_KEY. Revisa tu archivo .env")
        else:
            # Esto te confirmará en consola que la key se cargó (ofuscada por seguridad)
            logger.info(f"🔑 API Key cargada: {self.api_key[:6]}...{self.api_key[-4:]}")

        self.modelos_fallback = [
            "google/gemini-2.0-flash-lite-preview-02-05:free", # Agregamos este que es más estable
            "openrouter/free",
            "stepfun/step-3.5-flash:free",
            "upstage/solar-pro-3:free",
            "arcee-ai/trinity-large-preview:free"
        ]

    async def enviar_prompt(self, system_prompt: str, user_prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api", # Usa tu URL de repo o localhost
            "X-Title": "Constructor AI Analisis",
            "Content-Type": "application/json"
        }

        # Intentamos cada modelo de la lista
        for modelo in self.modelos_fallback:
            print(f"DEBUG: Intentando con modelo: {modelo}...")
            
            payload = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                #"response_format": { "type": "json_object" }
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

                    # Si el status es 200 y no hay error en el body, ¡éxito!
                    if response.status_code == 200 and "error" not in datos:
                        print(f"✅ ÉXITO con modelo: {modelo}")
                        return datos
                    
                    # Si hay error, lo logueamos y seguimos al siguiente modelo
                    error_info = datos.get("error", {}).get("message", "Error desconocido")
                    print(f"❌ FALLÓ {modelo}: {error_info}")
                    
                    # Pequeña pausa para no saturar
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"⚠️ Error de conexión con {modelo}: {str(e)}")
                continue

        # Si llegamos aquí, es que ninguno funcionó
        return {"error": {"message": "Ningún modelo de la lista de fallback respondió correctamente."}}
import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        # Lista de modelos por orden de prioridad (del mejor al más estable)
        self.modelos_fallback = [
            "openrouter/free",              # El automático por excelencia
            "stepfun/step-3.5-flash:free",  # Muy rápido y estable
            "upstage/solar-pro-3:free",     # Excelente razonamiento
            "arcee-ai/trinity-large-preview:free",
            "liquid/lfm-2.5-1.2b-thinking:free"
        ]

    async def enviar_prompt(self, system_prompt: str, user_prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Constructor AI",
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
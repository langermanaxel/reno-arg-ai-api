import httpx
from app.core.logging import get_logger

logger = get_logger(__name__)

class WebhookClient:
    async def notificar_finalizacion(self, analisis_id: str, proyecto_code: str, estado: str):
        # URL de ejemplo del Backend Principal
        url_webhook = "https://backend-principal.com/api/webhook/analisis-completado"
        
        payload = {
            "analisis_id": str(analisis_id),
            "proyecto_codigo": proyecto_code,
            "estado": estado,
            "resultado_url": f"https://tu-api-ia.com/api/analisis/{analisis_id}"
        }

        try:
            async with httpx.AsyncClient() as client:
                # Intentamos avisar al cliente. Usamos timeout corto para no trabar nuestra API
                response = await client.post(url_webhook, json=payload, timeout=5.0)
                logger.info(f"📡 Webhook enviado: Status {response.status_code}")
        except Exception as e:
            logger.error(f"⚠️ No se pudo enviar el Webhook: {str(e)}")
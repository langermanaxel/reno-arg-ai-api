"""Notificaciones webhook."""

import logging
from sqlalchemy.orm import Session
from app.services.webhook_client import WebhookClient
from app.models import EstadoAnalisis

logger = logging.getLogger(__name__)

class WebhookNotifier:
    def __init__(self, db: Session):
        self.db = db
        self.client = WebhookClient()

    async def notificar(self, analisis_id: int, proyecto_codigo: str):
        """Notifica finalización."""
        try:
            await self.client.notificar_finalizacion(
                analisis_id, proyecto_codigo, EstadoAnalisis.COMPLETADO
            )
            logger.info(f"📱 Webhook enviado: {analisis_id}")
        except Exception as e:
            logger.warning(f"⚠️ Webhook falló (no crítico): {e}")

import json
import logging
import httpx
from sqlalchemy.orm import Session
from uuid import UUID

from app.config import settings
from app.models import Analisis, ResultadoAnalisis, ObservacionGenerada
from app.schemas.snapshot import SnapshotInput
from app.models.enums import EstadoAnalisis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_engine")

class AIEngineService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.openrouter_api_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    async def procesar_analisis_completo(self, analisis_id: UUID, snapshot: SnapshotInput):
        analisis = self.db.query(Analisis).filter(Analisis.id == analisis_id).first()
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(snapshot)

        logger.info(f"🤖 Enviando análisis técnico {analisis_id} a {settings.llm_model}...")
        try:
            raw_response = await self._call_llm(system_prompt, user_prompt)
            data_ia = self._parse_ia_response(raw_response)
            
            # Guardar en las columnas narrativas de ResultadoAnalisis
            self._save_results(analisis_id, data_ia)
            
            analisis.estado = EstadoAnalisis.COMPLETADO
            logger.info(f"✅ Informe narrativo generado para {analisis_id}.")
            
        except Exception as e:
            analisis.estado = EstadoAnalisis.ERROR
            analisis.error_mensaje = str(e)
            logger.error(f"❌ Error en AI Engine: {e}")
        
        self.db.commit()

    def _get_system_prompt(self) -> str:
        return """
        Sos analista técnico de obras. Generás informes profesionales en formato narrativo, tono formal y objetivo. 
        Usá exclusivamente los datos del JSON recibido. No inventes información. 
        Si falta un dato, indicarlo como pendiente o no informado. 

        DEBES RESPONDER EXCLUSIVAMENTE UN JSON con esta estructura:
        {
            "proyecto": "Nombre",
            "periodo": "MM/AAAA",
            "fecha_generacion": "DD/MM/AAAA",
            "resumen_general": "Texto narrativo...",
            "ejecucion_planificacion": "Texto narrativo...",
            "seguridad_cumplimiento": "Texto narrativo...",
            "validaciones_tecnicas": "Texto narrativo...",
            "observacion_final": "Texto narrativo...",
            "score_coherencia": 0-100
        }
        No uses listas de puntos. Todo debe ser prosa formal.
        """

    def _build_user_prompt(self, snapshot: SnapshotInput) -> str:
        # mode='json' convierte automáticamente objetos date/uuid a strings
        s = snapshot.model_dump(mode='json')
        
        return f"""
        Analiza los siguientes datos de obra:
        Proyecto: {s.get('proyecto_nombre')} ({s.get('proyecto_codigo')})
        Responsable: {s.get('responsable_nombre')}
        Periodo: {s.get('periodo_mes')}/{s.get('periodo_anio')}
        Etapa: {s.get('etapa_nombre')} ({s.get('estado_etapa')}) - Avance: {s.get('porcentaje_avance')}%
        Avance Detallado: {s.get('detalle_avance')}
        Seguridad: {s.get('detalle_seguridad')}
        Validación: {s.get('detalle_validacion')}
        """

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

    def _parse_ia_response(self, raw_content: str) -> dict:
        return json.loads(raw_content)

    def _save_results(self, analisis_id: UUID, data: dict):
        # Mapeamos el JSON narrativo a las columnas de la tabla
        resultado = ResultadoAnalisis(
            analisis_id=analisis_id,
            resumen_general=data.get("resumen_general"),
            estado_ejecucion=data.get("ejecucion_planificacion"),
            estado_planificacion="Analizado s/ avances", # O lo que prefieras
            estado_seguridad=data.get("seguridad_cumplimiento"),
            estado_validaciones=data.get("validaciones_tecnicas"),
            observaciones_finales=data.get("observacion_final"),
            score_coherencia=data.get("score_coherencia", 0)
        )
        self.db.add(resultado)
"""Procesamiento LLM + auditoría."""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.utils.helpers import parse_json_seguro
from app.models import InvocacionLLM, PromptGenerado, RespuestaLLM, ResultadoAnalisis, ObservacionGenerada

logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()

    async def procesar_con_ia(self, analisis_id: int, datos: Dict):
        """Flujo completo IA: prompt → llamada → parse → resultados."""
        # 1. Construir prompts
        system_p, user_p = self.prompt_builder.construir_instrucciones(datos)
        
        # 2. Crear invocación
        invocacion = self._crear_invocacion(analisis_id)
        self.db.add(PromptGenerado(
            invocacion_id=invocacion.id, 
            system_prompt=system_p, 
            user_prompt=user_p
        ))
        self.db.flush()
        
        # 3. Llamar LLM
        start_time = datetime.now(timezone.utc)
        respuesta_raw = await self.llm_client.enviar_prompt(system_p, user_p)
        end_time = datetime.now(timezone.utc)
        
        # 4. Guardar + resultados
        self._guardar_respuesta_llm(invocacion, respuesta_raw, start_time, end_time)
        self._guardar_resultados(invocacion, respuesta_raw)
        
        logger.info(f"🤖 IA completada: {invocacion.id}")

    def _crear_invocacion(self, analisis_id: int) -> InvocacionLLM:
        invocacion = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado="gpt-4o-mini",
            invocado_at=datetime.now(timezone.utc)
        )
        self.db.add(invocacion)
        self.db.flush()
        return invocacion

    def _guardar_respuesta_llm(self, invocacion: InvocacionLLM, respuesta_raw: Dict, 
                             start: datetime, end: datetime):
        invocacion.duracion_ms = int((end - start).total_seconds() * 1000)
        
        if "choices" not in respuesta_raw:
            invocacion.exitosa = False
            invocacion.error_detalle = str(respuesta_raw)
            self.db.commit()
            raise Exception("Fallo IA")
        
        contenido = respuesta_raw['choices'][0]['message']['content']
        invocacion.tokens_prompt = respuesta_raw.get("usage", {}).get("prompt_tokens")
        invocacion.tokens_respuesta = respuesta_raw.get("usage", {}).get("completion_tokens")
        invocacion.exitosa = True
        
        parseado = parse_json_seguro(contenido)
        self.db.add(RespuestaLLM(
            invocacion_id=invocacion.id,
            respuesta_raw=contenido,
            respuesta_parseada=parseado
        ))

    def _guardar_resultados(self, invocacion: InvocacionLLM, respuesta_raw: Dict):
        contenido = parse_json_seguro(respuesta_raw['choices'][0]['message']['content'])
        
        resultado = ResultadoAnalisis(
            analisis_id=invocacion.analisis_id,
            resumen_general=contenido.get('resumen'),
            score_coherencia=contenido.get('score_coherencia'),
            detecta_riesgos=len(contenido.get('riesgos', [])) > 0
        )
        self.db.add(resultado)
        self.db.flush()
        
        for riesgo in contenido.get('riesgos', []):
            self.db.add(ObservacionGenerada(
                resultado_id=resultado.id,
                titulo=riesgo.get('titulo'),
                descripcion=riesgo.get('descripcion'),
                nivel=riesgo.get('nivel')
            ))

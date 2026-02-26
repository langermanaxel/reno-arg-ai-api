"""Procesamiento LLM + auditoría."""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.utils.helpers import parse_json_seguro
from app.models import (
    InvocacionLLM, 
    PromptGenerado, 
    RespuestaLLM, 
    ResultadoAnalisis, 
    ObservacionGenerada
)
from app.core.logging import get_logger

logger = get_logger(__name__)

class LLMProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()

    async def procesar_con_ia(self, analisis_id: Any, datos: Dict):
        """Flujo completo IA: prompt → llamada → parse → resultados."""
        
        # 1. Validación de datos mínimos para evitar prompts vacíos (None)
        if not datos or not isinstance(datos, dict):
            logger.warning(f"⚠️ Datos insuficientes para el análisis {analisis_id}. Abortando IA.")
            return

        # 2. Construir prompts (ahora pasan el JSON real)
        system_p, user_p = self.prompt_builder.construir_instrucciones(datos)
        
        # 3. Crear registro de invocación (Auditoría)
        invocacion = self._crear_invocacion(analisis_id)
        
        self.db.add(PromptGenerado(
            invocacion_id=invocacion.id, 
            system_prompt=system_p, 
            user_prompt=user_p
        ))
        self.db.flush() # Para asegurar que el prompt existe antes de la llamada
        
        # 4. Llamada al LLM con medición de tiempo
        start_time = datetime.now(timezone.utc)
        try:
            respuesta_raw = await self.llm_client.enviar_prompt(system_p, user_p)
            end_time = datetime.now(timezone.utc)
            
            # 5. Persistir respuesta y procesar resultados
            self._guardar_respuesta_llm(invocacion, respuesta_raw, start_time, end_time)
            self._guardar_resultados(invocacion, respuesta_raw)
            
            logger.info(f"🤖 IA completada con éxito para análisis: {analisis_id}")
            
        except Exception as e:
            invocacion.exitosa = False
            invocacion.error_detalle = str(e)
            self.db.commit()
            logger.error(f"❌ Fallo en procesamiento IA: {e}")
            raise e

    def _crear_invocacion(self, analisis_id: Any) -> InvocacionLLM:
        """Crea el registro inicial de la llamada a la IA."""
        invocacion = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado="fallback_orchestrator", # El cliente maneja la rotación
            exitosa=True,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(invocacion)
        self.db.flush()
        return invocacion

    def _guardar_respuesta_llm(self, invocacion: InvocacionLLM, respuesta_raw: Dict, 
                               start: datetime, end: datetime):
        """Actualiza la auditoría con los tokens y la duración."""
        invocacion.duracion_ms = int((end - start).total_seconds() * 1000)
        
        if "choices" not in respuesta_raw:
            invocacion.exitosa = False
            invocacion.error_detalle = "Respuesta de IA no contiene 'choices'"
            self.db.flush()
            return

        contenido = respuesta_raw['choices'][0]['message']['content']
        usage = respuesta_raw.get("usage", {})
        
        invocacion.tokens_prompt = usage.get("prompt_tokens")
        invocacion.tokens_respuesta = usage.get("completion_tokens")
        invocacion.total_tokens = usage.get("total_tokens")
        
        # Guardar el texto crudo recibido
        self.db.add(RespuestaLLM(
            invocacion_id=invocacion.id,
            respuesta_raw=contenido,
            respuesta_parseada=parse_json_seguro(contenido)
        ))
        self.db.flush()

    def _guardar_resultados(self, invocacion: InvocacionLLM, respuesta_raw: Dict):
        """Parsea el JSON de la IA y lo mapea a las tablas de resultados técnicos."""
        contenido_str = respuesta_raw['choices'][0]['message']['content']
        data = parse_json_seguro(contenido_str)
        
        if not data:
            logger.error("No se pudo parsear el contenido de la IA como JSON.")
            return

        # 🛡️ DEFENSA: Evitar el CheckConstraint del score_coherencia
        # Si tu DB pide >= 50, aquí podrías forzarlo, pero lo ideal es score real >= 0
        raw_score = data.get('score_coherencia', 0)
        score_final = max(0, min(100, int(raw_score))) 

        # Crear el objeto de resultado principal
        resultado = ResultadoAnalisis(
            analisis_id=invocacion.analisis_id,
            resumen_general=data.get('resumen', 'Sin resumen disponible'),
            score_coherencia=score_final,
            detecta_riesgos=len(data.get('riesgos', [])) > 0
        )
        self.db.add(resultado)
        self.db.flush()
        
        # Guardar cada riesgo identificado
        for riesgo in data.get('riesgos', []):
            observacion = ObservacionGenerada(
                resultado_id=resultado.id,
                titulo=riesgo.get('titulo', 'Riesgo no titulado'),
                descripcion=riesgo.get('descripcion', 'Sin descripción'),
                nivel=riesgo.get('nivel', 'INFORMATIVO').upper()
            )
            self.db.add(observacion)
        
        self.db.flush()
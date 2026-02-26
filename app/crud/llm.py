"""Procesamiento LLM + auditoría."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.utils.helpers import parse_json_seguro
from app.models import (
    InvocacionLLM,
    PromptGenerado,
    RespuestaLLM,
    ResultadoAnalisis,
    ObservacionGenerada,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.llm_client = LLMClient()
        self.prompt_builder = PromptBuilder()

    async def procesar_con_ia(
        self,
        analisis_id: Any,
        datos: Dict,
        model: Optional[str] = None,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None,
        instrucciones_extra: Optional[str] = None,
    ):
        """Flujo completo IA: prompt → llamada → auditoría → resultados."""

        if not datos or not isinstance(datos, dict):
            logger.warning(f"⚠️ Datos insuficientes para {analisis_id}. Abortando.")
            return

        # 1. Construir prompts respetando los parámetros del caller
        system_p, user_p = self.prompt_builder.construir_instrucciones(
            datos_entrada=datos,
            system_prompt=system_prompt,
            instrucciones_extra=instrucciones_extra,
        )

        # 2. Registro de invocación — modelo tentativo, se actualiza tras la llamada
        invocacion = self._crear_invocacion(analisis_id, model or "fallback_orchestrator")

        self.db.add(PromptGenerado(
            invocacion_id=invocacion.id,
            system_prompt=system_p,
            user_prompt=user_p,
        ))
        self.db.flush()

        # 3. Llamada al LLM con todos los parámetros configurados
        start_time = datetime.now(timezone.utc)
        try:
            respuesta_raw = await self.llm_client.enviar_prompt(
                system_prompt=system_p,
                user_prompt=user_p,
                modelo=model,
                temperature=temperature,
            )
            end_time = datetime.now(timezone.utc)

            # 4. Actualizar modelo real usado (puede ser el fallback, no el solicitado)
            invocacion.modelo_usado = respuesta_raw.get("model", model or "desconocido")

            # 5. Persistir auditoría y resultados
            self._guardar_respuesta_llm(invocacion, respuesta_raw, start_time, end_time)
            self._guardar_resultados(invocacion, respuesta_raw)

            # 6. Commit final — único punto de escritura confirmada
            self.db.commit()

            logger.info(f"✅ IA completada para análisis: {analisis_id} | modelo: {invocacion.modelo_usado}")

        except Exception as e:
            self.db.rollback()
            invocacion_id = getattr(invocacion, "id", None)
            logger.error(f"❌ Fallo en procesamiento IA [{analisis_id}]: {e}")

            # Re-abrir sesión limpia para persistir el error
            try:
                invocacion.exitosa = False
                invocacion.error_detalle = str(e)
                self.db.add(invocacion)
                self.db.commit()
            except Exception as db_err:
                logger.error(f"No se pudo persistir el error en DB: {db_err}")

            raise

    def _crear_invocacion(self, analisis_id: Any, modelo_inicial: str) -> InvocacionLLM:
        """Crea el registro inicial de auditoría."""
        invocacion = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado=modelo_inicial,   # se sobreescribe con el modelo real post-llamada
            exitosa=True,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(invocacion)
        self.db.flush()
        return invocacion

    def _guardar_respuesta_llm(
        self,
        invocacion: InvocacionLLM,
        respuesta_raw: Dict,
        start: datetime,
        end: datetime,
    ):
        """Auditoría completa: tokens, duración, costo y contenido crudo."""
        invocacion.duracion_ms = int((end - start).total_seconds() * 1000)

        if "choices" not in respuesta_raw:
            invocacion.exitosa = False
            invocacion.error_detalle = "Respuesta sin 'choices'"
            self.db.flush()
            return

        contenido = respuesta_raw["choices"][0]["message"]["content"]
        usage = respuesta_raw.get("usage", {})

        invocacion.tokens_prompt = usage.get("prompt_tokens")
        invocacion.tokens_respuesta = usage.get("completion_tokens")
        invocacion.total_tokens = usage.get("total_tokens")
        invocacion.costo_usd = usage.get("cost")   # ← campo de OpenRouter

        self.db.add(RespuestaLLM(
            invocacion_id=invocacion.id,
            respuesta_raw=contenido,
            respuesta_parseada=parse_json_seguro(contenido),
        ))
        self.db.flush()

    def _guardar_resultados(self, invocacion: InvocacionLLM, respuesta_raw: Dict):
        """Parsea la respuesta y persiste resultados + observaciones."""
        choices = respuesta_raw.get("choices", [])
        if not choices:
            logger.error("Sin 'choices' en respuesta — nada que persistir")
            return

        contenido_str = choices[0].get("message", {}).get("content", "")
        data = parse_json_seguro(contenido_str)

        # Si el LLM devolvió texto narrativo (no JSON), guardarlo como resumen directo
        if not data:
            resultado = ResultadoAnalisis(
                analisis_id=invocacion.analisis_id,
                resumen_general=contenido_str or "Sin contenido",
                score_coherencia=None,
                detecta_riesgos=False,
            )
            self.db.add(resultado)
            self.db.flush()
            logger.info("📝 Respuesta narrativa guardada como resumen directo")
            return

        # Respuesta JSON estructurada
        raw_score = data.get("score_coherencia", 0)
        try:
            score_final = max(0, min(100, int(float(raw_score))))
        except (ValueError, TypeError):
            score_final = None

        resultado = ResultadoAnalisis(
            analisis_id=invocacion.analisis_id,
            resumen_general=(
                data.get("resumen")
                or data.get("resumen_general")
                or "Sin resumen disponible"
            ),
            score_coherencia=score_final,
            detecta_riesgos=len(data.get("riesgos", [])) > 0,
        )
        self.db.add(resultado)
        self.db.flush()

        for riesgo in data.get("riesgos", []):
            nivel_raw = str(riesgo.get("nivel", "INFORMATIVO")).upper()
            self.db.add(ObservacionGenerada(
                resultado_id=resultado.id,
                titulo=riesgo.get("titulo", "Riesgo sin título"),
                descripcion=riesgo.get("descripcion", "Sin descripción"),
                nivel=nivel_raw,
            ))

        self.db.flush()
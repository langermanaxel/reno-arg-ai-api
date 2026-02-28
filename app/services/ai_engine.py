import json
import logging
import httpx
from sqlalchemy.orm import Session
from uuid import UUID
import asyncio

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

        logger.info(f"🤖 Iniciando análisis técnico {analisis_id}...")
        try:
            raw_response = await self._call_llm_with_fallback(system_prompt, user_prompt)
            data_ia = self._parse_ia_response(raw_response)
            self._save_results(analisis_id, data_ia)
            analisis.estado = EstadoAnalisis.COMPLETADO
            logger.info(f"✅ Informe narrativo generado para {analisis_id}.")

        except Exception as e:
            analisis.estado = EstadoAnalisis.ERROR
            analisis.error_mensaje = str(e)
            logger.error(f"❌ Error en AI Engine: {e}")

        self.db.commit()

    async def _call_llm_with_fallback(self, system_prompt: str, user_prompt: str) -> str:
        """
        Itera AVAILABLE_MODELS en orden. El primer modelo que responde
        correctamente gana; si falla, pasa al siguiente.
        """
        models = settings.available_models
        last_error = None

        for model in models:
            try:
                result = await self._call_llm(system_prompt, user_prompt, model=model)
                logger.info(f"✅ Modelo exitoso: {model}")
                return result
            except Exception as e:
                logger.warning(f"⚠️  {model} falló: {e}. Probando siguiente...")
                last_error = e

        raise Exception(f"Todos los modelos del registro fallaron. Último error: {last_error}")

    async def _call_llm(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        model = model or settings.available_models[0]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }

        max_retries = 2
        for attempt in range(max_retries):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url, headers=headers, json=payload, timeout=60.0
                )
                if response.status_code == 429:
                    wait = 2 ** attempt * 5
                    logger.warning(
                        f"⏳ Rate limit en {model}, reintentando en {wait}s "
                        f"(intento {attempt + 1}/{max_retries})..."
                    )
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
            
                content = response.json()["choices"][0]["message"]["content"]
            
                # ← Validar que el contenido no esté vacío
                if not content or not content.strip():
                    raise Exception(f"Respuesta vacía del modelo {model}.")
            
                return content

        raise Exception(f"Rate limit agotado para {model}.")

    def _get_system_prompt(self) -> str:
        return """
        Sos analista técnico de obras. Generás informes profesionales en formato narrativo, tono formal y objetivo.
        Usá exclusivamente los datos recibidos. No inventes información.
        Si falta un dato, indicarlo como pendiente o no informado.

        DEBES RESPONDER EXCLUSIVAMENTE UN JSON con esta estructura exacta:
        {
            "resumen_general": "Texto narrativo del estado general del proyecto...",
            "estado_ejecucion": "Texto narrativo sobre avance y ejecución de tareas...",
            "estado_planificacion": "Texto narrativo sobre cumplimiento de etapas y plazos...",
            "estado_seguridad": "Texto narrativo sobre condiciones de seguridad e higiene...",
            "estado_validaciones": "Texto narrativo sobre validaciones técnicas pendientes y aprobadas...",
            "riesgos_identificados": ["Riesgo 1", "Riesgo 2"],
            "score_coherencia": 85
        }
        No uses listas de puntos en los campos de texto. Todo debe ser prosa formal.
        riesgos_identificados debe ser una lista de strings concisos, puede estar vacía [].
        score_coherencia debe ser un número entero entre 0 y 100.
        """

    def _build_user_prompt(self, snapshot: SnapshotInput) -> str:
        s = snapshot.model_dump(mode='json')
        p = s.get('proyecto', {})
        avances = s.get('avances', [])
        etapas = s.get('etapas', [])
        ultimo_avance = avances[-1] if avances else {}

        etapas_texto = "\n".join([
            f"  - {e.get('etapa_nombre')} (orden {e.get('etapa_orden')}): "
            f"{e.get('estado')} | {e.get('fecha_inicio_estimada')} → {e.get('fecha_fin_estimada')}"
            for e in etapas
        ])

        avances_texto = "\n".join([
            f"  - {a.get('fecha_registro')} | {a.get('etapa_nombre')} | "
            f"{a.get('porcentaje_avance')}% | "
            f"Tareas: {', '.join(a.get('tareas_principales', []))} | "
            f"Oficios: {', '.join(a.get('oficios_activos', []))}"
            for a in avances
        ])

        # seguridad_higiene y validaciones_tecnicas son List[Any] — normalizamos a string
        seguridad_texto = '; '.join([
            str(item) if not isinstance(item, dict) else json.dumps(item, ensure_ascii=False)
            for item in s.get('seguridad_higiene', [])
        ])

        validaciones_texto = '; '.join([
            str(item) if not isinstance(item, dict) else json.dumps(item, ensure_ascii=False)
            for item in s.get('validaciones_tecnicas', [])
        ])

        return f"""
        Analiza los siguientes datos de obra:

        PROYECTO:
        Nombre: {p.get('proyecto_nombre')}
        Responsable técnico: {p.get('responsable_tecnico_nombre')}
        Ubicación: {p.get('ubicacion')}
        Tipo de intervención: {p.get('tipo_intervencion')}
        Superficie: {p.get('superficie_m2')} m²
        Sistema constructivo: {p.get('sistema_constructivo')}
        Fecha inicio: {p.get('fecha_inicio')}

        ETAPAS PLANIFICADAS:
{etapas_texto}

        HISTORIAL DE AVANCES:
{avances_texto}

        ETAPA Y AVANCE ACTUAL:
        Etapa: {ultimo_avance.get('etapa_nombre')} — {ultimo_avance.get('porcentaje_avance')}%
        Tareas: {', '.join(ultimo_avance.get('tareas_principales', []))}
        Oficios activos: {', '.join(ultimo_avance.get('oficios_activos', []))}

        SEGURIDAD E HIGIENE:
        {seguridad_texto}

        VALIDACIONES TÉCNICAS:
        {validaciones_texto}
        """

    def _parse_ia_response(self, raw_content: str) -> dict:
        # Algunos modelos envuelven el JSON en ```json ... ```
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())

    def _save_results(self, analisis_id: UUID, data: dict):
        resultado = ResultadoAnalisis(
            analisis_id=analisis_id,
            resumen_general=data.get("resumen_general", "No informado"),
            estado_ejecucion=data.get("estado_ejecucion", "No informado"),
            estado_planificacion=data.get("estado_planificacion", "No informado"),
            estado_seguridad=data.get("estado_seguridad", "No informado"),
            estado_validaciones=data.get("estado_validaciones", "No informado"),
            riesgos_identificados=data.get("riesgos_identificados", []),
            score_coherencia=data.get("score_coherencia", 0)
        )
        self.db.add(resultado)
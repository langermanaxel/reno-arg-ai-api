import json
import re
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app.api.dependencies import get_db
from app.config.settings import settings
from app.db.base import Base # Necesario para reset-db
from app.models.analisis import (
    Analisis, SnapshotRecibido, EstadoAnalisis, 
    ResultadoAnalisis, ObservacionGenerada, 
    DatoProyecto, DatoEtapa, DatoAvance, DatoSeguridad,
    InvocacionLLM, PromptGenerado, RespuestaLLM
)
from app.schemas.snapshot import SnapshotCreate
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.services.webhook_client import WebhookClient

logger = logging.getLogger(__name__)

router = APIRouter()

# --- ENDPOINTS DE NEGOCIO ---

@router.post("/iniciar")
async def iniciar_analisis(snapshot_in: SnapshotCreate, db: Session = Depends(get_db)):
    """Inicia el proceso de persistencia de datos y análisis con IA."""
    logger.info(f"📥 Recibida solicitud para proyecto: {snapshot_in.proyecto_codigo}")
    
    # 0. CREACIÓN DEL REGISTRO PADRE
    nuevo_analisis = Analisis(
        proyecto_codigo=snapshot_in.proyecto_codigo, 
        estado=EstadoAnalisis.PROCESANDO
    )
    db.add(nuevo_analisis)
    db.flush() 

    try:
        # 1. NORMALIZACIÓN Y PERSISTENCIA DE DATOS ESTRUCTURADOS
        # Aseguramos que datos_json sea siempre un dict, incluso si viene de Pydantic
        datos_json = snapshot_in.datos
        if not isinstance(datos_json, dict):
            datos_json = datos_json.model_dump() if hasattr(datos_json, "model_dump") else dict(datos_json)

        nuevo_snapshot = SnapshotRecibido(
            analisis_id=nuevo_analisis.id,
            payload_completo=json.dumps(datos_json)
        )
        db.add(nuevo_snapshot)
        db.flush() 

        # --- Mapeo de Proyecto ---
        proy_data = datos_json.get("proyecto", {})
        db.add(DatoProyecto(
            snapshot_id=nuevo_snapshot.id,
            codigo=proy_data.get("codigo"),
            nombre=proy_data.get("nombre"),
            responsable_tecnico=proy_data.get("responsable_tecnico")
        ))

        # --- Mapeo de Etapas (Iteración robusta) ---
        for etapa in datos_json.get("etapas", []):
            # Soporta tanto dict como objetos
            e = etapa if isinstance(etapa, dict) else etapa
            db.add(DatoEtapa(
                snapshot_id=nuevo_snapshot.id,
                nombre=e.get("nombre") if isinstance(e, dict) else getattr(e, "nombre", None),
                estado=e.get("estado") if isinstance(e, dict) else getattr(e, "estado", None),
                avance_estimado=e.get("avance_estimado") if isinstance(e, dict) else getattr(e, "avance_estimado", 0)
            ))

        # --- Mapeo de Avances (Con corrección de fechas) ---
        for avance in datos_json.get("registros_avance", []):
            a = avance if isinstance(avance, dict) else avance
            fecha_str = a.get("fecha") if isinstance(a, dict) else getattr(a, "fecha", None)
            fecha_obj = datetime.now(timezone.utc).date() # Fallback a hoy
            
            if fecha_str:
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                    try:
                        fecha_obj = datetime.strptime(fecha_str, fmt).date()
                        break
                    except: continue

            db.add(DatoAvance(
                snapshot_id=nuevo_snapshot.id,
                fecha_registro=fecha_obj,
                supervisor=a.get("supervisor") if isinstance(a, dict) else getattr(a, "supervisor", None),
                porcentaje_avance=a.get("porcentaje_avance") if isinstance(a, dict) else getattr(a, "porcentaje_avance", 0),
                presenta_desvios=a.get("presenta_desvios", False) if isinstance(a, dict) else getattr(a, "presenta_desvios", False),
                tareas_ejecutadas=a.get("tareas_ejecutadas", []) if isinstance(a, dict) else getattr(a, "tareas_ejecutadas", []),
                oficios_activos=a.get("oficios_activos", []) if isinstance(a, dict) else getattr(a, "oficios_activos", [])
            ))

        # --- Mapeo de Seguridad ---
        lista_seguridad = datos_json.get("medidas_seguridad", [])
        if lista_seguridad:
            total = len(lista_seguridad)
            cumple = sum(1 for m in lista_seguridad if (m.get("cumple") if isinstance(m, dict) else getattr(m, 'cumple', False)) is True)
            db.add(DatoSeguridad(
                snapshot_id=nuevo_snapshot.id,
                fecha_registro=datetime.now(timezone.utc).date(),
                medidas_implementadas=lista_seguridad,
                total_medidas_chequeadas=total,
                cumple_todas=(total == cumple)
            ))

        # Hacemos el primer commit: Los datos de la obra ya están seguros
        db.commit()
        logger.info(f"✅ Datos de obra persistidos exitosamente para análisis {nuevo_analisis.id}")

        # 2. PROCESAMIENTO CON IA
        prompt_builder = PromptBuilder()
        system_p, user_p = prompt_builder.construir_instrucciones(datos_json)
        
        invocacion = InvocacionLLM(
            analisis_id=nuevo_analisis.id,
            modelo_usado="gpt-4o-mini",
            invocado_at=datetime.now(timezone.utc)
        )
        db.add(invocacion)
        db.flush()

        db.add(PromptGenerado(invocacion_id=invocacion.id, system_prompt=system_p, user_prompt=user_p))

        llm_client = LLMClient()
        start_time = datetime.now(timezone.utc)
        respuesta_raw = await llm_client.enviar_prompt(system_p, user_p)
        end_time = datetime.now(timezone.utc)

        invocacion.duracion_ms = int((end_time - start_time).total_seconds() * 1000)
        
        if "choices" not in respuesta_raw:
             invocacion.exitosa = False
             invocacion.error_detalle = str(respuesta_raw)
             db.commit()
             raise Exception("Fallo en respuesta de IA")

        string_contenido = respuesta_raw['choices'][0]['message']['content']
        invocacion.tokens_prompt = respuesta_raw.get("usage", {}).get("prompt_tokens")
        invocacion.tokens_respuesta = respuesta_raw.get("usage", {}).get("completion_tokens")
        invocacion.exitosa = True

        # Parseo de respuesta JSON de la IA (con regex de seguridad)
        contenido_ia = {}
        try:
            contenido_ia = json.loads(string_contenido)
        except:
            match = re.search(r"(\{.*\})", string_contenido, re.DOTALL)
            if match: contenido_ia = json.loads(match.group(1))

        db.add(RespuestaLLM(
            invocacion_id=invocacion.id, 
            respuesta_raw=string_contenido, 
            respuesta_parseada=contenido_ia
        ))

        # 3. GUARDADO DE RESULTADOS FINALES
        resultado = ResultadoAnalisis(
            analisis_id=nuevo_analisis.id,
            resumen_general=contenido_ia.get('resumen'),
            score_coherencia=contenido_ia.get('score_coherencia'),
            detecta_riesgos=len(contenido_ia.get('riesgos', [])) > 0
        )
        db.add(resultado)
        db.flush()

        for riesgo in contenido_ia.get('riesgos', []):
            db.add(ObservacionGenerada(
                resultado_id=resultado.id,
                titulo=riesgo.get('titulo'),
                descripcion=riesgo.get('descripcion'),
                nivel=riesgo.get('nivel')
            ))

        nuevo_analisis.estado = EstadoAnalisis.COMPLETADO
        db.commit()
        
        # 4. NOTIFICACIÓN (Webhook)
        try:
            webhook = WebhookClient()
            await webhook.notificar_finalizacion(nuevo_analisis.id, nuevo_analisis.proyecto_codigo, nuevo_analisis.estado)
        except Exception as e:
            logger.warning(f"⚠️ Webhook fallido (no crítico): {e}")

        return {"analisis_id": nuevo_analisis.id, "resultado": contenido_ia}

    except Exception as e:
        db.rollback() 
        nuevo_analisis.estado = EstadoAnalisis.ERROR
        db.add(nuevo_analisis) # Re-añadimos para poder actualizar el estado a ERROR
        db.commit()
        logger.error(f"❌ Error crítico en proceso de análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detalle/{analisis_id}")
async def obtener_analisis_completo(analisis_id: str, db: Session = Depends(get_db)):
    """Obtiene la radiografía completa de un análisis y su auditoría."""
    analisis = db.query(Analisis).options(
        joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.proyecto),
        joinedload(Analisis.snapshot).joinedload(SnapshotRecibido.etapas),
        joinedload(Analisis.resultado).joinedload(ResultadoAnalisis.observaciones),
        joinedload(Analisis.invocaciones).joinedload(InvocacionLLM.respuesta)
    ).filter(Analisis.id == analisis_id).first()

    if not analisis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return {
        "id": analisis.id,
        "estado": analisis.estado,
        "datos_obra": {
            "proyecto": analisis.snapshot.proyecto[0] if analisis.snapshot and analisis.snapshot.proyecto else None,
            "etapas_registradas": len(analisis.snapshot.etapas) if analisis.snapshot else 0
        },
        "auditoria_ia": [
            {
                "modelo": i.modelo_usado, 
                "exitoso": i.exitosa,
                "latencia_ms": i.duracion_ms,
                "total_tokens": (i.tokens_prompt or 0) + (i.tokens_respuesta or 0)
            } 
            for i in analisis.invocaciones
        ],
        "resultado_negocio": analisis.resultado
    }

# --- ENDPOINTS DE MANTENIMIENTO (PROTEGIDOS) ---

@router.post("/reset-db")
async def reset_database(
    x_admin_token: str = Header(None), 
    db: Session = Depends(get_db)
):
    """
    ⚠️ PELIGRO: Borra y recrea toda la base de datos.
    Solo disponible en desarrollo y con token válido.
    """
    if settings.ENV != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación no permitida en este entorno."
        )

    if x_admin_token != settings.ADMIN_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de administración inválido."
        )

    try:
        logger.warning("💣 Iniciando reset total de base de datos solicitado por administrador.")
        engine_db = db.get_bind()
        Base.metadata.drop_all(bind=engine_db)
        Base.metadata.create_all(bind=engine_db)
        return {"status": "success", "message": "Base de datos reseteada correctamente."}
    except Exception as e:
        logger.error(f"❌ Fallo crítico en reset-db: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al recrear esquemas.")
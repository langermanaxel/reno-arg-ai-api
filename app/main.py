import json, re
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.base import Base, engine, get_db
# Importamos todos los modelos, incluyendo las nuevas tablas de datos estructurados
from app.models.analisis import (
    Analisis, SnapshotRecibido, EstadoAnalisis, 
    ResultadoAnalisis, ObservacionGenerada, 
    DatoProyecto, DatoEtapa
)
from app.schemas.snapshot import SnapshotCreate
from app.services.llm_client import LLMClient
from app.services.prompt_builder import PromptBuilder
from app.services.webhook_client import WebhookClient
from app.utils.logger import logger

# Sincronizar tablas con la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Analisis API - Edición Profesional")

@app.get("/")
def read_root():
    return {"status": "API Online 🚀", "version": "2.0.0"}

# --- ENDPOINT: CONSULTA DE DETALLES (GET) ---
@app.get("/analisis/{analisis_id}")
async def obtener_detalle_analisis(analisis_id: str, db: Session = Depends(get_db)):
    # Usamos joinedload para evitar el problema de N+1 consultas en la DB
    analisis = db.query(Analisis).options(
        joinedload(Analisis.resultado).joinedload(ResultadoAnalisis.observaciones)
    ).filter(Analisis.id == analisis_id).first()

    if not analisis:
        raise HTTPException(status_code=404, detail="El análisis solicitado no existe.")

    return {
        "id": analisis.id,
        "proyecto": analisis.proyecto_codigo,
        "estado": analisis.estado,
        "fecha_creacion": analisis.fecha_solicitud,
        "resultado_ia": {
            "resumen": analisis.resultado.resumen_general if analisis.resultado else None,
            "score_coherencia": analisis.resultado.score_coherencia if analisis.resultado else 0,
            "riesgos": [
                {
                    "titulo": obs.titulo,
                    "nivel": obs.nivel,
                    "descripcion": obs.descripcion
                } for obs in (analisis.resultado.observaciones if analisis.resultado else [])
            ]
        }
    }

# --- ENDPOINT: INICIAR PROCESO (POST) ---
@app.post("/analisis/iniciar")
async def iniciar_analisis(snapshot_in: SnapshotCreate, db: Session = Depends(get_db)):
    logger.info(f"📥 Recibida solicitud para proyecto: {snapshot_in.proyecto_codigo}")
    
    # 1. Crear registro principal de Análisis
    nuevo_analisis = Analisis(
        proyecto_codigo=snapshot_in.proyecto_codigo, 
        estado=EstadoAnalisis.PROCESANDO
    )
    db.add(nuevo_analisis)
    db.flush() # Para obtener el UUID generado inmediatamente

    try:
        # 2. PERSISTENCIA DE DATOS (SNAPSHOT Y ESTRUCTURADOS)
        # Guardamos el JSON crudo original
        nuevo_snapshot = SnapshotRecibido(
            analisis_id=nuevo_analisis.id,
            payload_completo=json.dumps(snapshot_in.datos)
        )
        db.add(nuevo_snapshot)

        # Desnormalización: Extraemos info del JSON a tablas relacionales
        datos_json = snapshot_in.datos
        
        # Mapear Proyecto
        info_proy = datos_json.get("proyecto", {})

        # Si por error enviaron un string, lo ignoramos o manejamos
        if isinstance(info_proy, str):
            logger.warning(f"⚠️ El campo 'proyecto' vino como string: {info_proy}. Se esperaba un objeto.")
            info_proy = {} # Lo reseteamos a vacío para que no rompa el código

        db_proy = DatoProyecto(
            analisis_id=nuevo_analisis.id,
            codigo=info_proy.get("codigo"),
            nombre=info_proy.get("nombre"),
            responsable_tecnico=info_proy.get("responsable_tecnico")
        )
        db.add(db_proy)

        # 2. Mapear Etapas (Con validación de tipo)
        lista_etapas = datos_json.get("etapas", [])
        if isinstance(lista_etapas, list):
            for etapa in lista_etapas:
                if isinstance(etapa, dict): # Solo procesamos si es un objeto
                    db_etapa = DatoEtapa(
                        analisis_id=nuevo_analisis.id,
                        nombre=etapa.get("nombre"),
                        estado=etapa.get("estado"),
                        avance_estimado=etapa.get("avance_estimado")
                    )
                    db.add(db_etapa)
                else:
                    logger.warning(f"⚠️ Se saltó una etapa porque no es un objeto válido: {etapa}")
        
        # Guardamos la estructura inicial
        db.commit()
        logger.info(f"💾 Datos estructurados guardados para análisis {nuevo_analisis.id}")

        # 3. PROCESAMIENTO CON INTELIGENCIA ARTIFICIAL
        prompt_builder = PromptBuilder()
        system, user = prompt_builder.construir_instrucciones(snapshot_in.model_dump())
        
        llm_client = LLMClient()
        respuesta_raw = await llm_client.enviar_prompt(system, user)

        if "choices" not in respuesta_raw:
             raise Exception(respuesta_raw.get("error", {}).get("message", "Fallo total de modelos IA"))
        
        # Extraer y parsear contenido
        string_contenido = respuesta_raw['choices'][0]['message']['content']
        
        # ... después de recibir respuesta_raw ...
        string_contenido = respuesta_raw['choices'][0]['message']['content']
        
        # --- NUEVA LÓGICA DE LIMPIEZA DE JSON ---
        try:
            # 1. Intentamos parsear directo
            contenido_ia = json.loads(string_contenido)
        except json.JSONDecodeError:
            logger.warning("⚠️ La IA no devolvió JSON puro. Intentando extraer bloque JSON...")
            # 2. Si falla, buscamos algo que esté entre llaves { ... } usando Regex
            match = re.search(r"(\{.*\})", string_contenido, re.DOTALL)
            if match:
                try:
                    contenido_ia = json.loads(match.group(1))
                except:
                    raise Exception("La IA devolvió un JSON mal formado que no pudo ser reparado.")
            else:
                logger.error(f"Respuesta cruda de la IA: {string_contenido}")
                raise Exception("La IA no devolvió ningún formato JSON válido.")
        # ---------------------------------------

        # 4. PERSISTENCIA DEL RESULTADO DE IA
        resultado = ResultadoAnalisis(
            analisis_id=nuevo_analisis.id,
            resumen_general=contenido_ia.get('resumen'),
            score_coherencia=contenido_ia.get('score_coherencia'),
            detecta_riesgos=len(contenido_ia.get('riesgos', [])) > 0
        )
        db.add(resultado)
        db.flush()

        for riesgo in contenido_ia.get('riesgos', []):
            obs = ObservacionGenerada(
                resultado_id=resultado.id,
                titulo=riesgo.get('titulo'),
                descripcion=riesgo.get('descripcion'),
                nivel=riesgo.get('nivel')
            )
            db.add(obs)

        # Finalizar estado
        nuevo_analisis.estado = EstadoAnalisis.COMPLETADO
        db.commit()
        logger.info(f"✅ Análisis {nuevo_analisis.id} finalizado exitosamente")

        # 5. NOTIFICACIÓN EXTERNA (WEBHOOK)
        webhook = WebhookClient()
        await webhook.notificar_finalizacion(
            analisis_id=nuevo_analisis.id, 
            proyecto_code=nuevo_analisis.proyecto_codigo, 
            estado=nuevo_analisis.estado
        )

        return {
            "mensaje": "Análisis completo, datos persistidos y notificados", 
            "analisis_id": nuevo_analisis.id,
            "resultado": contenido_ia
        }

    except Exception as e:
        db.rollback() 
        nuevo_analisis.estado = EstadoAnalisis.ERROR
        db.commit()
        logger.error(f"❌ Error en análisis {nuevo_analisis.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(e)}")
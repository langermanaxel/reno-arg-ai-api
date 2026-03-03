from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.snapshot import SnapshotCreate
from app.crud.analisis import AnalisisCRUD
from app.crud.queries import get_analisis_completo
from app.core.logging import get_logger

from app.core.settings.base import settings

import uuid
import random

import json
import logging


router = APIRouter()

DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.3

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_DICT = {
    "role": "system",
    "content": (
        "Sos analista técnico de obras. "
        "Generás informes profesionales en formato narrativo, tono formal y objetivo. "
        "Usá exclusivamente los datos del JSON recibido. "
        "No inventes información. "
        "Si falta un dato, indicarlo como pendiente o no informado. "
        "Estructura obligatoria: "
        "Proyecto, Período analizado (mes/año), Fecha de generación (última fecha relevante), "
        "Resumen general del estado de la obra, Ejecución y planificación, "
        "Medidas de seguridad y cumplimiento, Validaciones técnicas, Observación general. "
        "No usar listas. "
        "Retornar estrictamente un único JSON válido."
    ),
}


async def procesar_analisis(
    analisis_id: str,
    datos: dict,
    db: Session,
    model: str = DEFAULT_MODEL,
):
    crud = AnalisisCRUD(db)
    temperature = DEFAULT_TEMPERATURE

    try:
        # Guardar snapshot original
        crud.guardar_snapshot(analisis_id, datos)

        # Asegurar que datos sean 100% serializables
        datos_json_safe = json.dumps(
            jsonable_encoder(datos),
            ensure_ascii=False,
        )
        messages = [
            SYSTEM_PROMPT_DICT,
            {
                "role": "user",
                "content": datos_json_safe,
            },
        ]
        respuesta_ia = await crud.llm_processor.procesar_con_ia(
            analisis_id=analisis_id,
            messages=messages,
            model=model,
            temperature=temperature,
        )
        crud.marcar_completado(analisis_id)
        db.commit()

        return respuesta_ia

    except Exception as e:
        db.rollback()
        crud.marcar_error(analisis_id, str(e))
        db.commit()
        raise


@router.post("/iniciar", status_code=200)
async def iniciar_analisis(
    snapshot_in: SnapshotCreate,
    db: Session = Depends(get_db),
):
    crud = AnalisisCRUD(db)

    try:
        # Crear registro padre
        analisis = crud.crear_registro_padre(snapshot_in.project.codigo)
        db.commit()
        db.refresh(analisis)

        analisis_id = str(analisis.id)

        # Convertir Pydantic → dict JSON-safe
        datos_dict = jsonable_encoder(snapshot_in)

        # Procesar IA sincrónicamente
        resultado = await procesar_analisis(
            analisis_id=analisis_id,
            datos=datos_dict,
            db=db,
        )

        return {
            "analisis_id": analisis_id,
            "status": "completed",
            "resultado": resultado,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detalle/{analisis_id}")
async def obtener_analisis_completo(
    analisis_id: str,
    db: Session = Depends(get_db),
):
    resultado = get_analisis_completo(db, analisis_id)

    if not resultado:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return resultado
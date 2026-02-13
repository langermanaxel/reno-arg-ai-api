from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import Base, engine, get_db
from app.models.analisis import Analisis, SnapshotRecibido, EstadoAnalisis
from app.schemas.snapshot import SnapshotCreate
import json

# Crear tablas en la DB (Esto evita usar Alembic por ahora)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Analisis API")

@app.post("/analisis/iniciar")
def iniciar_analisis(snapshot_in: SnapshotCreate, db: Session = Depends(get_db)):
    # 1. Crear el Analisis
    nuevo_analisis = Analisis(
        proyecto_codigo=snapshot_in.proyecto_codigo,
        estado=EstadoAnalisis.PENDIENTE
    )
    db.add(nuevo_analisis)
    db.flush() # Genera el ID sin cerrar la transacción

    # 2. Guardar el Snapshot
    nuevo_snapshot = SnapshotRecibido(
        analisis_id=nuevo_analisis.id,
        payload_completo=json.dumps(snapshot_in.datos)
    )
    db.add(nuevo_snapshot)
    
    # 3. Guardar cambios
    db.commit()
    db.refresh(nuevo_analisis)

    return {
        "mensaje": "Analisis iniciado correctamente",
        "analisis_id": str(nuevo_analisis.id),
        "estado": nuevo_analisis.estado
    }

@app.get("/")
def read_root():
    return {"status": "API Online 🚀"}
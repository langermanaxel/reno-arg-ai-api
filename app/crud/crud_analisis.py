from sqlalchemy.orm import Session
from uuid import UUID
from app.models.analysis import Analisis
from app.schemas.analisis import AnalisisCreate
from app.models.enums import EstadoAnalisis

def create_analisis(db: Session, analisis_in: AnalisisCreate) -> Analisis:
    db_obj = Analisis(
        proyecto_codigo=analisis_in.proyecto_codigo,
        periodo_desde=analisis_in.periodo_desde,
        periodo_hasta=analisis_in.periodo_hasta,
        estado=EstadoAnalisis.PENDIENTE
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_analisis(db: Session, analisis_id: UUID) -> Analisis | None:
    return db.query(Analisis).filter(Analisis.id == analisis_id).first()

def update_estado(db: Session, analisis_id: UUID, estado: EstadoAnalisis) -> Analisis | None:
    db_obj = get_analisis(db, analisis_id)
    if db_obj:
        db_obj.estado = estado
        db.commit()
        db.refresh(db_obj)
    return db_obj
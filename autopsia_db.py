import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.analisis import Analisis, DatoProyecto, DatoEtapa, DatoAvance, DatoSeguridad
from app.schemas.snapshot import SnapshotCreate
from app.api.v1.endpoints.analisis import iniciar_analisis
from unittest.mock import AsyncMock, patch

# DB en memoria para no romper nada
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

MOCK_DATA = {
    "proyecto_codigo": "TEST-TABLAS",
    "datos": {
        "proyecto": {"codigo": "P1", "nombre": "Obra Test", "responsable_tecnico": "Ing. Mock"},
        "etapas": [{"nombre": "Cimientos", "estado": "en_progreso", "avance_estimado": 25}],
        "registros_avance": [{"fecha": "2026-02-22", "supervisor": "Tester", "porcentaje_avance": 10}],
        "medidas_seguridad": [{"nombre": "Arnés", "cumple": True}]
    }
}

async def correr_autopsia():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("\n🚀 INICIANDO AUTOPSIA DE PERSISTENCIA...")
    
    # Mockeamos el envío a la IA para que no falle por falta de API KEY
    with patch("app.services.llm_client.LLMClient.enviar_prompt", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = {
            "choices": [{"message": {"content": '{"resumen": "Ok", "score_coherencia": 100, "riesgos": []}'}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }
        
        snapshot_in = SnapshotCreate(**MOCK_DATA)
        try:
            await iniciar_analisis(snapshot_in=snapshot_in, db=db)
            print("✅ Simulación de análisis completada.")
        except Exception as e:
            print(f"❌ Error durante el análisis: {e}")

    # REPORTE FINAL
    print("\n📊 RESULTADO DE TABLAS:")
    print(f"---------------------------------")
    print(f"Registros en DatoProyecto:  {db.query(DatoProyecto).count()}")
    print(f"Registros en DatoEtapa:     {db.query(DatoEtapa).count()}")
    print(f"Registros en DatoAvance:    {db.query(DatoAvance).count()}")
    print(f"Registros en DatoSeguridad: {db.query(DatoSeguridad).count()}")
    print(f"---------------------------------")
    
    if db.query(DatoEtapa).count() == 0:
        print("⚠️ ALERTA: La tabla de Etapas está vacía. Revisa el bucle en analisis.py")

if __name__ == "__main__":
    asyncio.run(correr_autopsia())
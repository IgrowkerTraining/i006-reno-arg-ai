import logging

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import engine, get_db, Base
from app.core.config import settings
from app.schemas import BodyBase, AnalisisResponse
from app.services import AuditService, AIService
from app.repositories import UnitOfWork

logger = logging.getLogger(__name__)

# Solo para desarrollo local — en producción usar Alembic para migraciones
if settings.is_development:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RENO Studio AI - Construction Audit",
    description="API modularizada para auditoría técnica de obras civiles.",
    version="1.0.0",
)

ai_client = AIService()


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    uow = UnitOfWork(db)
    return AuditService(uow, ai_client)


@app.post(
    "/v1/analisis/procesar",
    response_model=AnalisisResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auditoría"],
)
async def create_analysis(
    payload: BodyBase,
    service: AuditService = Depends(get_audit_service),
) -> AnalisisResponse:
    """Ejecuta el proceso completo de auditoría técnica para un proyecto."""
    try:
        return await service.ejecutar_proceso_completo(payload)
    except ValueError as e:
        # Error de negocio esperado (ej: JSON inválido de la IA)
        logger.warning("Error de validación en análisis: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        # Error inesperado — se loggea internamente, no se expone al cliente
        logger.exception("Error inesperado al procesar análisis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el procesamiento. Contacte al administrador.",
        )


@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)) -> dict:
    """Verifica el estado del servicio y la conexión a la base de datos."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        logger.exception("Health check: fallo en la conexión a la base de datos")
        db_status = "unavailable"

    return {"status": "ok", "database": db_status}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
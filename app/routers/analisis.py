from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas import BodyBase, AnalisisResponse
from app.services import AuditService, AIService
from app.repositories import UnitOfWork

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/analisis", tags=["Auditoría"])

# Instancia global del servicio de IA (o podrías inyectarla)
ai_client = AIService()

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    uow = UnitOfWork(db)
    return AuditService(uow, ai_client)

@router.post(
    "/procesar",
    response_model=AnalisisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_analysis(
    payload: BodyBase,
    service: AuditService = Depends(get_audit_service),
) -> AnalisisResponse:
    try:
        return await service.ejecutar_proceso_completo(payload)
    except ValueError as e:
        logger.warning("Error de validación en análisis: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception:
        logger.exception("Error inesperado al procesar análisis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el procesamiento.",
        )
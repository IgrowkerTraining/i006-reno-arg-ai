import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import engine, get_db, Base
from app.core.config import settings
from app.schemas import BodyBase, AnalisisResponse  # ← fix 1
from app.services import AuditService, AIService
from app.repositories import UnitOfWork

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RENO Studio AI - Construction Audit",
    description="API modularizada para auditoría técnica de obras civiles.",
    version="1.0.0"
)

ai_client = AIService()

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    uow = UnitOfWork(db)
    return AuditService(uow, ai_client)

@app.post(
    "/v1/analisis/procesar",
    response_model=AnalisisResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auditoría"]
)
async def create_analysis(
    payload: BodyBase,  # ← fix 1
    service: AuditService = Depends(get_audit_service)
):
    try:
        respuesta_backend = await service.ejecutar_proceso_completo(payload)  # ← fix 2
        return respuesta_backend  # ← fix 3
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en el procesamiento: {str(e)}"
        )

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
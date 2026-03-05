import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 1. Importaciones de Infraestructura y Configuración
from app.core.database import engine, get_db, Base
from app.core.config import settings

# 2. Importaciones de Esquemas (Contratos de API)
from app.schemas import ConstructionPayload, AnalisisResponse

# 3. Importaciones de Lógica de Negocio (Modularizada)
from app.services import AuditService, AIService
from app.repositories import UnitOfWork

# Crear las tablas en la base de datos al iniciar (Opcional si usas Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RENO Studio AI - Construction Audit",
    description="API modularizada para auditoría técnica de obras civiles.",
    version="1.0.0"
)

# --- Inyección de Dependencias ---

# Instanciamos el servicio de IA una sola vez (Singleton) para optimizar recursos
ai_client = AIService()

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """
    Fabrica el servicio de auditoría inyectando el Unit of Work 
    y el cliente de IA pre-configurado.
    """
    uow = UnitOfWork(db)
    return AuditService(uow, ai_client)

# --- Endpoints ---

@app.post(
    "/v1/analisis/procesar", 
    response_model=AnalisisResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Auditoría"]
)
async def create_analysis(
    payload: ConstructionPayload, 
    service: AuditService = Depends(get_audit_service)
):
    """
    Endpoint principal para procesar una auditoría de obra.
    Delega toda la lógica de negocio al Service Layer.
    """
    try:
        analisis_id, informe = await service.ejecutar_proceso_completo(payload)
        
        return {
            "analisis_id": analisis_id,
            "status": "COMPLETADO",
            "proyecto_codigo": payload.project.codigo,
            "resultado": informe
        }
    except Exception as e:
        # El error ya fue registrado en la DB por el Service antes de lanzar la excepción
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error interno en el procesamiento: {str(e)}"
        )

@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "database": "connected"}

# --- Ejecución ---

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
import uvicorn
from fastapi import FastAPI
from app.core.database import engine, Base
from app.core.config import settings
from app.routers import analisis_router, sistema_router  # Importamos los routers

# Migraciones automáticas (Solo desarrollo)
if settings.is_development:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RENO Studio AI - Construction Audit",
    description="API modularizada para auditoría técnica de obras civiles.",
    version="1.0.0",
)

# Registro de rutas
app.include_router(analisis_router)
app.include_router(sistema_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
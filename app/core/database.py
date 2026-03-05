from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Configuración del Motor
# pool_pre_ping asegura que la conexión sea válida antes de usarla
engine = create_engine(
    settings.DATABASE_URL, 
    pool_pre_ping=True
)

# 2. Generador de Sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base para los modelos
Base = declarative_base()

# 4. Dependencia de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
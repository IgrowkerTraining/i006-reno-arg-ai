from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings


# ─── Base declarativa (SQLAlchemy 2.0) ───────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Motor ────────────────────────────────────────────────────────────────────
# pool_pre_ping valida la conexión antes de usarla, evitando errores por
# conexiones que el servidor de BD cerró por inactividad.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# ─── Generador de sesiones ────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Dependencia de FastAPI ───────────────────────────────────────────────────
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
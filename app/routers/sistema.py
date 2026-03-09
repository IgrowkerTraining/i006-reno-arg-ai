from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Sistema"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        logger.exception("Health check: fallo en la base de datos")
        db_status = "unavailable"

    return {"status": "ok", "database": db_status}
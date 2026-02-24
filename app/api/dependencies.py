<<<<<<< HEAD
"""API dependencies and utilities."""

from fastapi import HTTPException, status
from typing import Optional

from app.services.ai_service import ai_service
from app.core.logging import get_logger

logger = get_logger(__name__)


async def get_ai_service():
    """Get AI service instance."""
    try:
        # Check if AI service is healthy
        if not await ai_service.health_check():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is currently unavailable"
            )
        return ai_service
    except Exception as e:
        logger.error(f"AI service dependency error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to AI service"
        )
=======
# app/api/dependencies.py
from typing import Generator
from app.db.base import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> fuente_api/main

<<<<<<< HEAD
"""Logging configuration for the application."""

import logging
import sys
from typing import Optional

from app.config.settings import settings


def setup_logging() -> None:
    """Configure application logging."""
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name or __name__)
=======
import logging
import sys
from app.config.settings import settings

def setup_logging():
    # Eliminamos configuraciones previas para evitar duplicidad
    logging.root.handlers = []
    
    logging.basicConfig(
        level=settings.LOGGING_LEVEL, # Nivel dinámico desde el .env
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )

# Logger para usar en el resto de la aplicación
logger = logging.getLogger("app")
>>>>>>> fuente_api/main

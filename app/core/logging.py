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

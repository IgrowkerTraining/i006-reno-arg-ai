from .analisis import router as analisis_router
from .sistema import router as sistema_router

# Esto permite que otros archivos vean estas variables directamente
__all__ = ["analisis_router", "sistema_router"]
from app.models import Analisis, EstadoAnalisis
from .base_repository import BaseRepository

class AuditRepository(BaseRepository[Analisis]):
    def __init__(self, db):
        # Le pasamos a la base la sesión y el modelo específico
        super().__init__(db, Analisis)

    def crear(self, proyecto_codigo, desde, hasta) -> Analisis:
        analisis = Analisis(
            proyecto_codigo=proyecto_codigo,
            periodo_desde=desde,
            periodo_hasta=hasta
        )
        self.db.add(analisis)
        self.db.flush()
        return analisis

    def actualizar_estado(self, analisis_id: int, estado: str, error_msg: str = None):
        # Ahora podrías usar self.get_by_id(analisis_id) gracias a la base
        analisis = self.get_by_id(analisis_id)
        if analisis:
            analisis.estado = estado
            if error_msg:
                analisis.error_mensaje = error_msg
            self.db.flush()
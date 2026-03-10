from typing import Optional
from app.models import Analisis, EstadoAnalisis
from .base import BaseRepository


class AuditRepository(BaseRepository[Analisis]):
    def __init__(self, db):
        super().__init__(db, Analisis)
        
# def crear(self, proyecto_codigo: str, desde, hasta) -> Analisis:
    def crear(self, proyecto_codigo: str, desde, hasta) -> Analisis:
        analisis = Analisis(
            proyecto_codigo=proyecto_codigo,
            periodo_desde=desde,
            periodo_hasta=hasta,
        )
        self.db.add(analisis)
        self.db.flush()
        return analisis

    def actualizar_estado(
        self,
        analisis_id: int,
        estado: EstadoAnalisis,
        error_msg: Optional[str] = None,
    ) -> None:
        analisis = self.get_by_id(analisis_id)
        if analisis:
            analisis.estado = estado
            if error_msg:
                analisis.error_mensaje = error_msg
            self.db.flush()
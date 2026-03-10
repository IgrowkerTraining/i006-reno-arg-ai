from app.models import SnapshotRecibido
from .base import BaseRepository


class SnapshotRepository(BaseRepository[SnapshotRecibido]):
    def __init__(self, db):
        super().__init__(db, SnapshotRecibido)

    def guardar(self, analisis_id: int, payload_dict: dict) -> None:
        snapshot = SnapshotRecibido(
            analisis_id=analisis_id,
            payload_completo=payload_dict,
        )
        self.db.add(snapshot)
        self.db.flush()
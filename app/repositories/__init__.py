from .audit_repository import AuditRepository
from .snapshot_repository import SnapshotRepository
from .llm_repository import LLMRepository
from sqlalchemy.orm import Session

class UnitOfWork:
    """Contenedor para agrupar repositorios bajo una misma transacción"""
    def __init__(self, db: Session):
        self.db = db
        self.audits = AuditRepository(db)
        self.snapshots = SnapshotRepository(db)
        self.llm = LLMRepository(db)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
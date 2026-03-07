from sqlalchemy.orm import Session

from .audit_repository import AuditRepository
from .snapshot_repository import SnapshotRepository
from .llm_repository import LLMRepository


class UnitOfWork:
    """
    Agrupa repositorios bajo una misma transacción de base de datos.

    Uso recomendado como context manager:

        with UnitOfWork(db) as uow:
            uow.audits.registrar(...)
            uow.snapshots.guardar(...)
        # commit automático al salir sin excepciones
        # rollback automático si ocurre una excepción
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.audits = AuditRepository(db)
        self.snapshots = SnapshotRepository(db)
        self.llm = LLMRepository(db)

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Si hubo una excepción se deshacen los cambios; si no, se confirman
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        """Confirma todos los cambios pendientes en la transacción actual."""
        try:
            self.db.commit()
        except Exception as e:
            self.rollback()
            raise RuntimeError("Error al confirmar la transacción") from e

    def rollback(self) -> None:
        """Deshace todos los cambios pendientes en la transacción actual."""
        self.db.rollback()
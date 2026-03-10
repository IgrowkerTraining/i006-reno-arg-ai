from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.orm import Session
from app.core.database import Base

# Acotamos al tipo Base real para que el linter pueda inferir el tipo concreto en cada subclase
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
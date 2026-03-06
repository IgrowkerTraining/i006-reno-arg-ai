from typing import TypeVar, Generic, Type, Optional  # ← sacar List, Any
from sqlalchemy.orm import Session

T = TypeVar("T")  # ← bound=Any es redundante, Any es el default

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()
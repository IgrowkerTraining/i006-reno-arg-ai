from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
# Importamos Base desde donde la definiste en el core
from app.core.database import Base 

# Usamos 'Any' para evitar que el linter se queje de la expresión dinámica
T = TypeVar("T", bound=Any) 

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        # El linter ahora reconocerá T como el tipo del modelo
        return self.db.query(self.model).filter(self.model.id == id).first()
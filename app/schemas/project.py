from pydantic import BaseModel

class ProyectoBase(BaseModel):
    codigo: str
    nombre: str
from pydantic import BaseModel, validator
from typing import List, Dict
from datetime import date
from .project import ProyectoBase

class ConstructionPayload(BaseModel):
    project: ProyectoBase
    periodo: Dict[str, date]
    etapas: List[Dict]
    registros_avance: List[Dict]
    medidas_seguridad: List[Dict]
    validaciones_tecnicas: List[Dict]

    # Convierte automáticamente {} → [{}] si viene un objeto suelto
    @validator("etapas", "registros_avance", "medidas_seguridad", "validaciones_tecnicas", pre=True, each_item=False)
    def wrap_if_not_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v
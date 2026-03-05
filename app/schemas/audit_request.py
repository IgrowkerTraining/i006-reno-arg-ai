from pydantic import BaseModel
from typing import List, Dict
from datetime import date
from .project import ProyectoBase # Importación relativa

class ConstructionPayload(BaseModel):
    project: ProyectoBase
    periodo: Dict[str, date]
    etapas: List[Dict]
    registros_avance: List[Dict]
    medidas_seguridad: List[Dict]
    validaciones_tecnicas: List[Dict]
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date


class Proyecto(BaseModel):
    codigo: str
    nombre: str
    responsable_tecnico: Optional[str] = None


class Periodo(BaseModel):
    desde: date
    hasta: date


class Etapa(BaseModel):
    nombre: str
    estado: str
    avance_estimado: Optional[int] = None


class RegistroAvance(BaseModel):
    fecha: date
    supervisor: Optional[str] = None
    tareas_ejecutadas: Optional[List[str]] = []
    oficios_activos: Optional[List[str]] = []
    porcentaje_avance: Optional[int] = None


class CoberturaART(BaseModel):
    entidad: str
    vigencia: str


class MedidaSeguridad(BaseModel):
    fecha: date
    implementadas: Optional[List[str]] = []
    cobertura_art: Optional[CoberturaART] = None


class ValidacionTecnica(BaseModel):
    fecha: date
    estado: str
    etapa: Optional[str] = None
    responsable: Optional[str] = None


# BodyBase al final, cuando todas las clases ya están definidas
class BodyBase(BaseModel):
    project: Proyecto
    periodo: Periodo
    etapas: List[Etapa]
    registros_avance: List[RegistroAvance]
    medidas_seguridad: List[MedidaSeguridad]
    validaciones_tecnicas: List[ValidacionTecnica]

    @field_validator("etapas", "registros_avance", "medidas_seguridad", "validaciones_tecnicas", mode="before")
    @classmethod
    def wrap_if_not_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v
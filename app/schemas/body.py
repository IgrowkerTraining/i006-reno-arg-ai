from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import date


class Proyecto(BaseModel):
    codigo: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    responsable_tecnico: str = Field(min_length=1)

    @field_validator("codigo", "nombre", "responsable_tecnico")
    @classmethod
    def no_debe_ser_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El campo no puede estar vacío ni contener solo espacios")
        return v.strip()


class Periodo(BaseModel):
    desde: date
    hasta: date

    @model_validator(mode="after")
    def desde_antes_que_hasta(self) -> "Periodo":
        if self.desde > self.hasta:
            raise ValueError("'desde' debe ser anterior a 'hasta'")
        return self


class Etapa(BaseModel):
    nombre: str
    estado: str
    avance_estimado: float


class RegistroAvance(BaseModel):
    fecha: date
    supervisor: str
    tareas_ejecutadas: List[str]
    oficios_activos: List[str]
    porcentaje_avance: float


class CoberturaART(BaseModel):
    entidad: str
    vigencia: str


class MedidaSeguridad(BaseModel):
    fecha: date
    implementadas: List[str]
    cobertura_art: CoberturaART


class ValidacionTecnica(BaseModel):
    fecha: date
    estado: str
    etapa: str
    responsable: str


# BodyBase al final, cuando todas las clases ya están definidas
class BodyBase(BaseModel):
    project: Proyecto
    periodo: Periodo
    etapas: List[Etapa]
    registros_avance: List[RegistroAvance]
    medidas_seguridad: MedidaSeguridad
    validaciones_tecnicas: ValidacionTecnica

    @field_validator("etapas", "registros_avance", mode="before")
    @classmethod
    def wrap_if_not_list(cls, v):
        # Permite recibir un objeto único en vez de una lista de uno
        if isinstance(v, dict):
            return [v]
        return v
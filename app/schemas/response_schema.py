from pydantic import BaseModel, ConfigDict, Field
from typing import Any

class DetalleResultado(BaseModel):
    # Usamos Field(alias=...) para que el JSON de salida tenga espacios y tildes
    proyecto: str = Field(alias="Proyecto")
    periodo: str = Field(alias="Período analizado")
    fecha: str = Field(alias="Fecha de generación")
    resumen: str = Field(alias="Resumen general del estado de la obra")
    ejecucion: str = Field(alias="Ejecución y planificación")
    seguridad: str = Field(alias="Medidas de seguridad y cumplimiento")
    validaciones: str = Field(alias="Validaciones técnicas")
    observacion: str = Field(alias="Observación general")

    # Configuración para permitir asignar valores usando los nombres de las variables
    model_config = ConfigDict(populate_by_name=True)

class AnalisisResponse(BaseModel):
    analisis_id: int
    status: str
    # Cambiamos str por el nuevo objeto DetalleResultado
    resultado: DetalleResultado

    model_config = ConfigDict(from_attributes=True)
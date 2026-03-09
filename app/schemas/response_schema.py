from pydantic import BaseModel, ConfigDict, Field
from app.models.enums_model import EstadoAnalisis
from uuid import UUID


class DetalleResultado(BaseModel):
    # Aliases simples y sin caracteres especiales para que el JSON de la IA
    # sea predecible. La presentación con tildes y espacios queda en el frontend.
    proyecto: str = Field(alias="proyecto")
    periodo: str = Field(alias="periodo_analizado")
    fecha: str = Field(alias="fecha_generacion")
    resumen: str = Field(alias="resumen_general")
    ejecucion: str = Field(alias="ejecucion_planificacion")
    seguridad: str = Field(alias="seguridad_cumplimiento")
    validaciones: str = Field(alias="validaciones_tecnicas")
    observacion: str = Field(alias="observacion_general")

    model_config = ConfigDict(populate_by_name=True)


class AnalisisResponse(BaseModel):
    analisis_id: UUID
    status: EstadoAnalisis
    resultado: DetalleResultado

    model_config = ConfigDict(from_attributes=True)
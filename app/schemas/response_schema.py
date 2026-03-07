from pydantic import BaseModel, ConfigDict, Field
from app.models.enums_model import EstadoAnalisis

class SeccionInforme(BaseModel):
    """Estructura para secciones del informe que la IA devuelve con estado y observaciones."""
    estado: str
    observaciones: list[str]


class DetalleResultado(BaseModel):
    # Aliases simples y sin caracteres especiales para que el JSON de la IA
    # sea predecible. La presentación con tildes y espacios queda en el frontend.
    proyecto: str = Field(alias="proyecto")
    periodo: str = Field(alias="periodo_analizado")
    fecha: str = Field(alias="fecha_generacion")
    resumen: str = Field(alias="resumen_general")
    ejecucion: SeccionInforme = Field(alias="ejecucion_planificacion")
    seguridad: SeccionInforme = Field(alias="seguridad_cumplimiento")
    validaciones: SeccionInforme = Field(alias="validaciones_tecnicas")
    observacion: str = Field(alias="observacion_general")

    model_config = ConfigDict(populate_by_name=True)


class AnalisisResponse(BaseModel):
    analisis_id: int
    status: EstadoAnalisis
    resultado: DetalleResultado

    model_config = ConfigDict(from_attributes=True)
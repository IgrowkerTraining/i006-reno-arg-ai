import enum

class EstadoAnalisis(str, enum.Enum):
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"
import enum

class EstadoAnalisis(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"
    CANCELADO = "CANCELADO"

class CategoriaObservacion(str, enum.Enum):
    EJECUCION = "EJECUCION"
    PLANIFICACION = "PLANIFICACION"
    SEGURIDAD = "SEGURIDAD"
    CUMPLIMIENTO = "CUMPLIMIENTO"
    RIESGO = "RIESGO"

class NivelObservacion(str, enum.Enum):
    INFORMATIVO = "INFORMATIVO"
    ATENCION = "ATENCION"
    CRITICO = "CRITICO"

class EstadoEtapa(str, enum.Enum):
    PLANIFICADA = "planificada"
    EN_EJECUCION = "en_ejecucion"
    FINALIZADA = "finalizada"
    PAUSADA = "pausada"

class NivelRiesgo(str, enum.Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

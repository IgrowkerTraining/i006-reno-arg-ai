from sqlalchemy import Column, String, DateTime, Integer, Text
from datetime import datetime
from app.core.database import Base
from .enums import EstadoAnalisis

class Analisis(Base):
    __tablename__ = "analisis"
    id = Column(Integer, primary_key=True, index=True)
    proyecto_codigo = Column(String, index=True)
    periodo_desde = Column(DateTime)
    periodo_hasta = Column(DateTime)
    estado = Column(String, default=EstadoAnalisis.PROCESANDO)
    error_mensaje = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
from sqlalchemy import Column, String, Date, DateTime, Integer, Text  # ← agregar Date
from datetime import datetime
from app.core.database import Base
from .enums_model import EstadoAnalisis

class Analisis(Base):
    __tablename__ = "analisis"
    id = Column(Integer, primary_key=True, index=True)
    proyecto_codigo = Column(String, index=True)
    periodo_desde = Column(Date)  # ← era DateTime
    periodo_hasta = Column(Date)  # ← era DateTime
    estado = Column(String, default=EstadoAnalisis.PROCESANDO)
    error_mensaje = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
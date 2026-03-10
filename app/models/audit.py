from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base  # ruta unificada para todos los modelos
from .enums import EstadoAnalisis


class Analisis(Base):
    __tablename__ = "analisis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proyecto_codigo = Column(String, nullable=False, index=True)
    periodo_desde = Column(DateTime(timezone=True), nullable=False)
    periodo_hasta = Column(DateTime(timezone=True), nullable=False)
    estado = Column(SAEnum(EstadoAnalisis), default=EstadoAnalisis.PROCESANDO, nullable=False)
    error_mensaje = Column(Text, nullable=True)
    fecha_creacion = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones — permiten acceso directo sin joins manuales
    snapshots = relationship("SnapshotRecibido", back_populates="analisis")
    invocaciones = relationship("InvocacionLLM", back_populates="analisis")
    resultado = relationship("ResultadoAnalisis", back_populates="analisis", uselist=False)
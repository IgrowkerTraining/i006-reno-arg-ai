from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base  # ruta unificada para todos los modelos


class SnapshotRecibido(Base):
    __tablename__ = "snapshots_recibidos"

    # id = Column(Integer, primary_key=True, index=True)
    # analisis_id = Column(
    #     Integer,
    #     ForeignKey("analisis.id", ondelete="CASCADE"),
    #     nullable=False,
    # )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, unique=True)
    payload_completo = Column(JSON, nullable=False)

    analisis = relationship("Analisis", back_populates="snapshots")
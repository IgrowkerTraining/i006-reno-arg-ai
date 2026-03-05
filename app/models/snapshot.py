from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.core.database import Base

class SnapshotRecibido(Base):
    __tablename__ = "snapshots_recibidos"
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(Integer, ForeignKey("analisis.id"))
    payload_completo = Column(JSON)
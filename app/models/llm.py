from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base  # ruta unificada para todos los modelos


class InvocacionLLM(Base):
    __tablename__ = "invocaciones_llm"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, unique=True)
    modelo_usado = Column(String, nullable=False)
    tokens_prompt = Column(Integer, nullable=False)
    tokens_respuesta = Column(Integer, nullable=False)
    exitosa = Column(Boolean, nullable=False)
    prompt_enviado = Column(JSON, nullable=True)

    analisis = relationship("Analisis", back_populates="invocaciones")


class ResultadoAnalisis(Base):
    __tablename__ = "resultados_analisis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analisis_id = Column(UUID(as_uuid=True), ForeignKey("analisis.id", ondelete="CASCADE"), nullable=False, unique=True)
    datos_informe = Column(JSON, nullable=False)

    analisis = relationship("Analisis", back_populates="resultado")
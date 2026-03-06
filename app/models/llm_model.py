from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON  # Requerido para datos estructurados
from app.core.database import Base

class InvocacionLLM(Base):
    __tablename__ = "invocaciones_llm"
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(Integer, ForeignKey("analisis.id"))
    modelo_usado = Column(String)
    tokens_prompt = Column(Integer)
    tokens_respuesta = Column(Integer)
    exitosa = Column(Boolean)
    prompt_enviado = Column(JSON, nullable=True)

class ResultadoAnalisis(Base):
    __tablename__ = "resultados_analisis"
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(Integer, ForeignKey("analisis.id"))
    # Cambiamos resumen_general (Text) por datos_informe (JSON)
    datos_informe = Column(JSON)
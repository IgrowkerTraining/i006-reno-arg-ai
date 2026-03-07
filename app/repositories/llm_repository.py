from typing import TypedDict

from sqlalchemy.orm import Session

from app.models import InvocacionLLM, ResultadoAnalisis


class MetaLLM(TypedDict):
    modelo: str
    tokens_prompt: int
    tokens_respuesta: int
    prompt: str | None


class LLMRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar_invocacion(self, analisis_id: int, meta: MetaLLM) -> InvocacionLLM:
        """Registra los datos de la invocación al LLM (modelo, tokens, prompt enviado)."""
        invocacion = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado=meta["modelo"],
            tokens_prompt=meta["tokens_prompt"],
            tokens_respuesta=meta["tokens_respuesta"],
            exitosa=True,
            prompt_enviado=meta.get("prompt"),
        )
        self.db.add(invocacion)
        return invocacion

    def registrar_resultado(self, analisis_id: int, informe: dict) -> ResultadoAnalisis:
        """Registra el informe generado por el LLM como resultado del análisis."""
        resultado = ResultadoAnalisis(
            analisis_id=analisis_id,
            datos_informe=informe,
        )
        self.db.add(resultado)
        return resultado

    def registrar_resultado_y_tokens(
        self,
        analisis_id: int,
        informe: dict,
        meta: MetaLLM,
    ) -> None:
        """
        Registra en una sola operación la invocación al LLM y el resultado del análisis.
        Hace flush al final para detectar errores antes del commit.
        """
        self.registrar_invocacion(analisis_id, meta)
        self.registrar_resultado(analisis_id, informe)

        try:
            self.db.flush()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(
                f"Error al registrar resultado del análisis {analisis_id}"
            ) from e
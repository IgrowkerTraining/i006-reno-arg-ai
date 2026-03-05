from sqlalchemy.orm import Session
from app.models import InvocacionLLM, ResultadoAnalisis

class LLMRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar_resultado_y_tokens(self, analisis_id: int, informe: str, meta: dict):
        inv = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado=meta['m'],
            tokens_prompt=meta['tp'],
            tokens_respuesta=meta['tr'],
            exitosa=True
        )
        res = ResultadoAnalisis(
            analisis_id=analisis_id, 
            resumen_general=informe
        )
        self.db.add(inv)
        self.db.add(res)
        self.db.flush()
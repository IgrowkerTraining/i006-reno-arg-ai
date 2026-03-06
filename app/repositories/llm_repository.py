from sqlalchemy.orm import Session
from app.models import InvocacionLLM, ResultadoAnalisis

class LLMRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar_resultado_y_tokens(self, analisis_id: int, informe: dict, meta: dict):
        inv = InvocacionLLM(
            analisis_id=analisis_id,
            modelo_usado=meta['m'],
            tokens_prompt=meta['tp'],
            tokens_respuesta=meta['tr'],
            exitosa=True,
            prompt_enviado=meta.get('prompt')  # ← 1. faltaba este campo
        )
        res = ResultadoAnalisis(
            analisis_id=analisis_id,
            datos_informe=informe  # ← 2. era resumen_general / 3. sin json.dumps
        )
        self.db.add(inv)
        self.db.add(res)
        self.db.flush()
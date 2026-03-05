import json
from app.repositories import UnitOfWork
from .ai_service import AIService

class AuditService:
    def __init__(self, uow: UnitOfWork, ai_service: AIService):
        self.uow = uow
        self.ai = ai_service

    async def ejecutar_proceso_completo(self, payload):
        # 1. Registro inicial
        analisis = self.uow.audits.crear(
            payload.project.codigo, payload.periodo["desde"], payload.periodo["hasta"]
        )
        payload_data = payload.model_dump(mode='json')
        self.uow.snapshots.guardar(analisis.id, payload_data)

        try:
            # 2. IA - Pedimos el informe
            response = await self.ai.pedir_informe(json.dumps(payload_data))
            raw_content = response.choices[0].message.content
            
            # 3. Parsear JSON (manejando si la IA devuelve bloques ```json)
            try:
                dict_resultado = json.loads(raw_content)
            except json.JSONDecodeError:
                # Limpieza de markdown por si la IA se pone creativa
                clean_json = raw_content.replace("```json", "").replace("```", "").strip()
                dict_resultado = json.loads(clean_json)

            # 4. Guardar en DB estructuradamente
            self.uow.llm.registrar_resultado_y_tokens(
                analisis.id, 
                dict_resultado, 
                {
                    'm': response.model, 
                    'tp': response.usage.prompt_tokens, 
                    'tr': response.usage.completion_tokens
                }
            )
            
            self.uow.audits.actualizar_estado(analisis.id, "COMPLETADO")
            self.uow.commit() 
            
            return analisis.id, dict_resultado

        except Exception as e:
            self.uow.rollback()
            self.uow.audits.actualizar_estado(analisis.id, "ERROR", error_msg=str(e))
            self.uow.commit()
            raise e
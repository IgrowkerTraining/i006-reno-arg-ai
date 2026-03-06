import json
import uuid
from datetime import datetime
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
            # 2. IA - Pedimos el informe (Llama a tu AIService anterior)
            response = await self.ai.pedir_informe(json.dumps(payload_data))
            raw_content = response.choices[0].message.content
            
            # 3. Parsear JSON (manejando si la IA devuelve bloques ```json)
            try:
                dict_resultado = json.loads(raw_content)
            except json.JSONDecodeError:
                clean_json = raw_content.replace("```json", "").replace("```", "").strip()
                dict_resultado = json.loads(clean_json)

            # Aseguramos que dict_resultado sea un dict (por si la IA devolvió una lista)
            if isinstance(dict_resultado, list) and len(dict_resultado) > 0:
                dict_resultado = dict_resultado[0]

            # 4. Mapear a la estructura final requerida por el backend
            # Extraemos los datos de la respuesta de la IA (dict_resultado)
            respuesta_backend = {
                "analisis_id": str(analisis.id),
                "status": "COMPLETADO",
                "resultado": {
                    "Proyecto": dict_resultado.get("Proyecto", "N/A"),
                    "Período analizado": dict_resultado.get("Período analizado", "N/A"),
                    "Fecha de generación": datetime.now().strftime("%Y-%m-%d"),
                    "Resumen general del estado de la obra": dict_resultado.get("Resumen general del estado de la obra", ""),
                    "Ejecución y planificación": dict_resultado.get("Ejecución y planificación", ""),
                    "Medidas de seguridad y cumplimiento": dict_resultado.get("Medidas de seguridad y cumplimiento", ""),
                    "Validaciones técnicas": dict_resultado.get("Validaciones técnicas", ""),
                    "Observación general": dict_resultado.get("Observación general", "")
                }
            }

            # 5. Guardar en DB (usamos el dict original o el mapeado según tu preferencia)
            self.uow.llm.registrar_resultado_y_tokens(
                analisis.id, 
                respuesta_backend["resultado"], 
                {
                    'm': response.model, 
                    'tp': response.usage.prompt_tokens, 
                    'tr': response.usage.completion_tokens
                }
            )
            
            self.uow.audits.actualizar_estado(analisis.id, "COMPLETADO")
            self.uow.commit() 
            
            return respuesta_backend

        except Exception as e:
            self.uow.rollback()
            # Si algo falla, el status cambia a ERROR
            self.uow.audits.actualizar_estado(analisis.id, "ERROR", error_msg=str(e))
            self.uow.commit()
            raise e
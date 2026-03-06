import re
import json
from datetime import datetime
from app.models import EstadoAnalisis
from app.repositories import UnitOfWork
from .ai_service import AIService

class AuditService:
    def __init__(self, uow: UnitOfWork, ai_service: AIService):
        self.uow = uow
        self.ai = ai_service

    async def ejecutar_proceso_completo(self, payload):
        # 1. Registro inicial
        analisis = self.uow.audits.crear(
            payload.project.codigo,
            payload.periodo.desde,
            payload.periodo.hasta
        )
        payload_data = payload.model_dump(mode='json')
        self.uow.snapshots.guardar(analisis.id, payload_data)

        try:
            # 2. IA
            response = await self.ai.pedir_informe(json.dumps(payload_data))
            raw_content = response.choices[0].message.content

            # 3. Parsear JSON
            try:
                dict_resultado = json.loads(raw_content)
            except json.JSONDecodeError:
                clean_json = raw_content.replace("```json", "").replace("```", "").strip()

                # Extraer solo el bloque JSON con regex por si la IA agrega texto extra
                match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                if match:
                    clean_json = match.group(0)

                try:
                    dict_resultado = json.loads(clean_json)
                except json.JSONDecodeError as e:
                    print(f"!!! RAW CONTENT DE LA IA:\n{raw_content}")
                    raise ValueError(f"La IA devolvió JSON inválido: {e}")

            if isinstance(dict_resultado, list) and len(dict_resultado) > 0:
                dict_resultado = dict_resultado[0]

            # 4. Mapear respuesta
            respuesta_backend = {
                "analisis_id": analisis.id,
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

            # 5. Guardar en DB
            self.uow.llm.registrar_resultado_y_tokens(
                analisis.id,
                respuesta_backend["resultado"],
                {
                    'm': response.model,
                    'tp': response.usage.prompt_tokens,
                    'tr': response.usage.completion_tokens,
                    'prompt': payload_data
                }
            )

            self.uow.audits.actualizar_estado(analisis.id, EstadoAnalisis.COMPLETADO)
            self.uow.commit()

            return respuesta_backend

        except Exception as e:
            self.uow.rollback()
            self.uow.audits.actualizar_estado(analisis.id, EstadoAnalisis.ERROR, error_msg=str(e))
            self.uow.commit()
            raise e
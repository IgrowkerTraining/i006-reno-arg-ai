import re
import json
import logging
from datetime import datetime, timezone

from app.models import EstadoAnalisis
from app.repositories import UnitOfWork
from .ai_service import AIService
from uuid import UUID


logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, uow: UnitOfWork, ai_service: AIService) -> None:
        self.uow = uow
        self.ai_service = ai_service

    async def ejecutar_proceso_completo(self, payload) -> dict:
        """
        Orquesta el flujo completo de auditoría:
        registro inicial → llamada a IA → parseo → persistencia → retorno.
        """
        analisis = self._registrar_analisis_inicial(payload)

        try:
            dict_resultado, response_meta = await self._obtener_resultado_ia(payload)
            respuesta_backend = self._mapear_resultado(analisis.id, dict_resultado)

            self._persistir_resultado(analisis.id, respuesta_backend["resultado"], payload, response_meta)
            self.uow.audits.actualizar_estado(analisis.id, EstadoAnalisis.COMPLETADO)
            self.uow.commit()

            return respuesta_backend

        except Exception as e:
            self._manejar_error(analisis.id, e)
            raise

    # -------------------------------------------------------------------------
    # Métodos privados
    # -------------------------------------------------------------------------

    def _registrar_analisis_inicial(self, payload) -> object:
        """Crea el registro de análisis y guarda el snapshot del payload."""
        analisis = self.uow.audits.crear(
            payload.project.codigo,
            payload.periodo.desde,
            payload.periodo.hasta,
        )
        payload_data = payload.model_dump(mode="json")
        self.uow.snapshots.guardar(analisis.id, payload_data)
        return analisis

    async def _obtener_resultado_ia(self, payload) -> tuple[dict, object]:
        """Llama al servicio de IA y retorna el resultado como diccionario."""
        payload_data = payload.model_dump(mode="json")
        response = await self.ai_service.pedir_informe(json.dumps(payload_data))
        raw_content = response.choices[0].message.content

        dict_resultado = self._parsear_json_respuesta(raw_content)

        # La IA a veces devuelve una lista con un único elemento
        if isinstance(dict_resultado, list) and len(dict_resultado) > 0:
            dict_resultado = dict_resultado[0]

        return dict_resultado, response

    def _parsear_json_respuesta(self, raw_content: str) -> dict:
        """
        Intenta parsear el JSON devuelto por la IA.
        Maneja el caso en que la IA envuelve el JSON en bloques de código markdown
        o agrega texto extra alrededor.
        """
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            pass

        clean = raw_content.replace("```json", "").replace("```", "").strip()

        # Extraer solo el bloque JSON por si la IA agrega texto antes o después
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            clean = match.group(0)

        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.error("Respuesta inválida de la IA:\n%s", raw_content)
            raise ValueError(f"La IA devolvió JSON inválido: {e}") from e

    def _mapear_resultado(self, analisis_id: UUID, dict_resultado: dict) -> dict:
        """Construye el diccionario de respuesta a partir del resultado de la IA."""
        print(dict_resultado)
        fecha_generacion = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        return {
            "analisis_id": analisis_id,
            "status": "COMPLETADO",
            "resultado": {
                "proyecto": dict_resultado.get("Proyecto", "N/A"),
                "periodo_analizado": dict_resultado.get("Período analizado", "N/A"),
                "fecha_generacion": fecha_generacion,
                "resumen_general": dict_resultado.get("Resumen general del estado de la obra", ""),
                "ejecucion_planificacion": dict_resultado.get("Ejecución y planificación", ""),
                "seguridad_cumplimiento": dict_resultado.get("Medidas de seguridad y cumplimiento", ""),
                "validaciones_tecnicas": dict_resultado.get("Validaciones técnicas", ""),
                "observacion_general": dict_resultado.get("Observación general", ""),
            },
        }

    def _persistir_resultado(self, analisis_id: UUID, resultado: dict, payload, response_meta) -> None:
        """Registra el resultado y los tokens de la invocación en la base de datos."""
        # print(response_meta)
        payload_data = payload.model_dump(mode="json")

        self.uow.llm.registrar_resultado_y_tokens(
            analisis_id,
            resultado,
            {
                "modelo": response_meta.model,
                "tokens_prompt": response_meta.usage.prompt_tokens,
                "tokens_respuesta": response_meta.usage.completion_tokens,
                "prompt": payload_data,
            },
        )

    def _manejar_error(self, analisis_id: UUID, error: Exception) -> None:
        """
        Deshace la transacción fallida y registra el estado de error del análisis
        en una transacción separada para no perder la trazabilidad.
        """
        self.uow.rollback()
        try:
            self.uow.audits.actualizar_estado(
                analisis_id,
                EstadoAnalisis.ERROR,
                error_msg=str(error),
            )
            self.uow.commit()
        except Exception:
            logger.exception(
                "No se pudo registrar el estado de error para el análisis %s",
                analisis_id,
            )
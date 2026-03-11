import re
import json
import logging
from datetime import datetime, timezone, date

from app.models import EstadoAnalisis
from app.repositories import UnitOfWork
from .ai import AIService
from uuid import UUID


logger = logging.getLogger(__name__)

CAMPOS_REQUERIDOS = [
    "Proyecto",
    "Período analizado",
    "Resumen general del estado de la obra",
    "Ejecución y planificación",
    "Medidas de seguridad y cumplimiento",
    "Validaciones técnicas",
    "Observación general",
]

MAX_REINTENTOS = 2

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

INFO_INSUFICIENTE = "Información insuficiente para generar informe."


class AuditService:
    def __init__(self, uow: UnitOfWork, ai_service: AIService) -> None:
        self.uow = uow
        self.ai_service = ai_service

    async def ejecutar_proceso_completo(self, payload) -> dict:
        """
        Orquesta el flujo completo de auditoría:
        registro inicial → llamada a IA → parseo → persistencia → retorno.
        Nunca propaga excepciones al caller: ante cualquier fallo retorna
        el formato esperado con los campos informativos correspondientes.
        """
        analisis = self._registrar_analisis_inicial(payload)

        try:
            payload_data = payload.model_dump(mode="json")
            dict_resultado, response_meta = await self._obtener_resultado_ia(payload, payload_data)
            respuesta_backend = self._mapear_resultado(analisis.id, dict_resultado, payload)

            self._persistir_resultado(analisis.id, respuesta_backend["resultado"], payload_data, response_meta)
            self.uow.audits.actualizar_estado(analisis.id, EstadoAnalisis.COMPLETADO)
            self.uow.commit()

        except Exception as e:
            logger.exception("Error en ejecutar_proceso_completo para análisis %s", analisis.id)
            respuesta_backend = self._mapear_resultado_error(analisis.id, payload)
            self._manejar_error(analisis.id, e)

        return respuesta_backend

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

    async def _obtener_resultado_ia(self, payload, payload_data: dict) -> tuple[dict, object]:
        """
        Llama al servicio de IA, valida los campos requeridos y, si hay campos
        faltantes o vacíos, reintenta hasta MAX_REINTENTOS veces enviándole
        a la IA exactamente qué campos debe completar.
        Retorna siempre un dict con todos los campos requeridos; los que no pudo
        completar la IA quedan con INFO_INSUFICIENTE.
        """
        data_json = json.dumps(payload_data)
        historial = self.ai_service.construir_mensajes_iniciales(data_json)
        response = await self.ai_service.pedir_informe(data_json)

        dict_resultado = {}

        for intento in range(MAX_REINTENTOS + 1):
            dict_resultado = self._extraer_dict_de_response(response)

            if dict_resultado is None:
                logger.warning("No se pudo extraer un dict válido de la respuesta de la IA.")
                dict_resultado = {}
                break

            campos_faltantes = self._detectar_campos_faltantes(dict_resultado)

            if not campos_faltantes:
                break

            if intento < MAX_REINTENTOS:
                logger.warning(
                    "Reintento %d/%d — campos faltantes o vacíos: %s",
                    intento + 1,
                    MAX_REINTENTOS,
                    campos_faltantes,
                )
                raw_content = response.choices[0].message.content
                historial = self._agregar_turno_correccion(historial, raw_content, campos_faltantes)
                response = await self.ai_service.pedir_correccion(historial)
            else:
                logger.warning(
                    "Se agotaron los reintentos. Campos sin completar: %s",
                    campos_faltantes,
                )

        # Rellena con INFO_INSUFICIENTE los campos que aún falten
        dict_resultado = self._completar_campos_faltantes(dict_resultado)

        return dict_resultado, response

    def _extraer_dict_de_response(self, response) -> dict | None:
        """
        Extrae y parsea el dict de la respuesta de la IA.
        Retorna None si la respuesta es irrecuperable.
        """
        if not response.choices:
            logger.warning("La IA no devolvió ninguna opción de respuesta (choices vacío).")
            return None

        raw_content = response.choices[0].message.content

        if not raw_content or not raw_content.strip():
            logger.warning("La IA devolvió una respuesta vacía o nula.")
            return None

        dict_resultado = self._parsear_json_respuesta(raw_content)

        if dict_resultado is None:
            return None

        if isinstance(dict_resultado, list):
            if not dict_resultado:
                logger.warning("La IA devolvió una lista vacía como resultado.")
                return None
            dict_resultado = dict_resultado[0]

        if not isinstance(dict_resultado, dict) or not dict_resultado:
            logger.warning(
                "La IA devolvió un resultado con formato inesperado o vacío: %s",
                type(dict_resultado),
            )
            return None

        return dict_resultado

    def _completar_campos_faltantes(self, dict_resultado: dict) -> dict:
        """Rellena con INFO_INSUFICIENTE los campos requeridos ausentes o vacíos."""
        for campo in CAMPOS_REQUERIDOS:
            if not dict_resultado.get(campo) or not str(dict_resultado[campo]).strip():
                dict_resultado[campo] = INFO_INSUFICIENTE
        return dict_resultado

    def _detectar_campos_faltantes(self, dict_resultado: dict) -> list[str]:
        """Retorna la lista de campos requeridos que están ausentes o vacíos."""
        return [
            campo
            for campo in CAMPOS_REQUERIDOS
            if not dict_resultado.get(campo) or not str(dict_resultado[campo]).strip()
        ]

    def _agregar_turno_correccion(
        self,
        historial: list[dict],
        respuesta_anterior: str,
        campos_faltantes: list[str],
    ) -> list[dict]:
        """
        Extiende el historial con la respuesta anterior de la IA y un nuevo mensaje
        de usuario indicando exactamente qué campos deben ser completados.
        """
        campos_formateados = "\n".join(f'  - "{campo}"' for campo in campos_faltantes)
        mensaje_correccion = (
            "Tu respuesta anterior está incompleta. "
            "Los siguientes campos están ausentes o tienen contenido vacío:\n"
            f"{campos_formateados}\n\n"
            "Por favor, devuelve nuevamente el JSON completo incluyendo todos los campos, "
            "asegurándote de que cada uno tenga contenido real y detallado."
        )

        return historial + [
            {"role": "assistant", "content": respuesta_anterior},
            {"role": "user", "content": mensaje_correccion},
        ]

    def _parsear_json_respuesta(self, raw_content: str) -> dict | None:
        """
        Intenta parsear el JSON devuelto por la IA.
        Maneja el caso en que la IA envuelve el JSON en bloques de código markdown
        o agrega texto extra alrededor.
        Retorna None en lugar de lanzar excepción si el JSON es irrecuperable.
        """
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            pass

        clean = raw_content.replace("```json", "").replace("```", "").strip()

        decoder = json.JSONDecoder()
        start = clean.find("{")
        if start != -1:
            try:
                result, _ = decoder.raw_decode(clean, start)
                return result
            except json.JSONDecodeError:
                pass

        logger.error("Respuesta inválida de la IA, no se pudo parsear el JSON:\n%s", raw_content)
        return None

    def _mapear_resultado(self, analisis_id: UUID, dict_resultado: dict, payload) -> dict:
        """
        Construye el diccionario de respuesta a partir del resultado de la IA.
        Si el período analizado no coincide con el solicitado, lo informa
        explícitamente en el campo correspondiente.
        """
        fecha_generacion = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        periodo_analizado = self._resolver_periodo_analizado(dict_resultado, payload)

        return {
            "analisis_id": analisis_id,
            "status": "COMPLETADO",
            "resultado": {
                "proyecto": dict_resultado.get("Proyecto", ""),
                "periodo_analizado": periodo_analizado,
                "fecha_generacion": fecha_generacion,
                "resumen_general": dict_resultado.get("Resumen general del estado de la obra", ""),
                "ejecucion_planificacion": dict_resultado.get("Ejecución y planificación", ""),
                "seguridad_cumplimiento": dict_resultado.get("Medidas de seguridad y cumplimiento", ""),
                "validaciones_tecnicas": dict_resultado.get("Validaciones técnicas", ""),
                "observacion_general": dict_resultado.get("Observación general", ""),
            },
        }

    def _mapear_resultado_error(self, analisis_id: UUID, payload) -> dict:
        """
        Construye el diccionario de respuesta ante un error irrecuperable,
        usando INFO_INSUFICIENTE en todos los campos de contenido.
        """
        fecha_generacion = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        desde: date = payload.periodo.desde
        periodo_solicitado = f"{MESES_ES[desde.month]} {desde.year}"

        return {
            "analisis_id": analisis_id,
            "status": "COMPLETADO",
            "resultado": {
                "proyecto": getattr(payload.project, "codigo", ""),
                "periodo_analizado": periodo_solicitado,
                "fecha_generacion": fecha_generacion,
                "resumen_general": INFO_INSUFICIENTE,
                "ejecucion_planificacion": INFO_INSUFICIENTE,
                "seguridad_cumplimiento": INFO_INSUFICIENTE,
                "validaciones_tecnicas": INFO_INSUFICIENTE,
                "observacion_general": INFO_INSUFICIENTE,
            },
        }

    def _resolver_periodo_analizado(self, dict_resultado: dict, payload) -> str:
        """
        Compara el período analizado por la IA con el solicitado en el payload.
        - Si coinciden: retorna el valor tal como lo devolvió la IA.
        - Si el período abarca más de un mes: retorna el valor de la IA sin validar.
        - Si no coinciden: informa el período encontrado en los registros para
          que el usuario sepa con qué datos fue generado el informe.
        """
        desde: date = payload.periodo.desde
        hasta: date = payload.periodo.hasta

        recibido = dict_resultado.get("Período analizado", "").strip()

        # Período multimenusal: no se valida, se retorna lo que devolvió la IA
        if desde.month != hasta.month or desde.year != hasta.year:
            logger.warning(
                "Período multimenusal, se omite validación estricta: %s → %s",
                desde,
                hasta,
            )
            return recibido or INFO_INSUFICIENTE

        esperado = f"{MESES_ES[desde.month]} {desde.year}"
        recibido_normalizado = self._normalizar_periodo(recibido)

        if recibido_normalizado.lower() == esperado.lower():
            logger.debug("Período analizado validado correctamente: '%s'", esperado)
            return esperado

        # Los registros de avance corresponden a un período distinto al solicitado
        logger.warning(
            "Período solicitado '%s' no coincide con el de los registros '%s'.",
            esperado,
            recibido_normalizado,
        )
        return (
            f"Se solicitó el informe para {esperado}, pero los registros de avance "
            f"disponibles corresponden a {recibido_normalizado}. "
            f"El informe fue generado con la información disponible."
        )

    def _normalizar_periodo(self, periodo: str) -> str:
        """
        Convierte distintos formatos de período a 'Mes Año'.
        Soporta:
          - "Abril 2026"              → "Abril 2026"  (ya normalizado)
          - "2026-04-01 a 2026-04-30" → "Abril 2026"
          - "2026-04-01"              → "Abril 2026"
        Si no puede parsear el formato, retorna el valor original.
        """
        match = re.search(r"(\d{4})-(\d{2})", periodo)
        if match:
            anio = int(match.group(1))
            mes = int(match.group(2))
            if 1 <= mes <= 12:
                return f"{MESES_ES[mes]} {anio}"
        return periodo

    def _persistir_resultado(self, analisis_id: UUID, resultado: dict, payload_data: dict, response_meta) -> None:
        """Registra el resultado y los tokens de la invocación en la base de datos."""
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
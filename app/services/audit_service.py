import re
import json
import logging
from datetime import datetime, timezone, date
import locale

from app.models import EstadoAnalisis
from app.repositories import UnitOfWork
from .ai_service import AIService
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
        """
        Llama al servicio de IA, valida los campos requeridos y, si hay campos
        faltantes o vacíos, reintenta hasta MAX_REINTENTOS veces enviándole
        a la IA exactamente qué campos debe completar.
        """
        payload_data = payload.model_dump(mode="json")
        data_json = json.dumps(payload_data)

        # Construye el historial inicial y lo reutiliza en cada reintento
        historial = self.ai_service.construir_mensajes_iniciales(data_json)

        response = await self.ai_service.pedir_informe(data_json)
        intentos = 0

        while True:
            # Verifica que choices no venga vacío
            if not response.choices:
                raise ValueError("La IA no devolvió ninguna opción de respuesta (choices vacío).")

            raw_content = response.choices[0].message.content

            # Verifica que el contenido no sea None ni cadena vacía
            if not raw_content or not raw_content.strip():
                raise ValueError("La IA devolvió una respuesta vacía o nula.")

            dict_resultado = self._parsear_json_respuesta(raw_content)

            # Si es lista, verifica que no esté vacía antes de extraer el primer elemento
            if isinstance(dict_resultado, list):
                if len(dict_resultado) == 0:
                    raise ValueError("La IA devolvió una lista vacía como resultado.")
                dict_resultado = dict_resultado[0]

            # Verifica que el resultado sea un dict y no esté vacío
            if not isinstance(dict_resultado, dict) or not dict_resultado:
                raise ValueError(
                    f"La IA devolvió un resultado con formato inesperado o vacío: {type(dict_resultado)}"
                )

            # Detecta campos faltantes o vacíos
            campos_faltantes = self._detectar_campos_faltantes(dict_resultado)

            if not campos_faltantes:
                # Todo OK — sale del loop
                self._validar_periodo_analizado(dict_resultado, payload)
                return dict_resultado, response

            # Si ya se agotaron los reintentos, lanza error
            if intentos >= MAX_REINTENTOS:
                raise ValueError(
                    f"La IA no completó los campos requeridos luego de {MAX_REINTENTOS} reintentos. "
                    f"Campos faltantes: {campos_faltantes}"
                )

            # Construye el mensaje de corrección y reintenta
            intentos += 1
            logger.warning(
                "Reintento %d/%d — campos faltantes o vacíos: %s",
                intentos,
                MAX_REINTENTOS,
                campos_faltantes,
            )

            historial = self._agregar_turno_correccion(historial, raw_content, campos_faltantes)
            response = await self.ai_service.pedir_correccion(historial)

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
    
    def _validar_periodo_analizado(self, dict_resultado: dict, payload) -> None:
        """
        Verifica que el 'Período analizado' devuelto por la IA
        coincida con el rango de fechas del payload.
        """
        desde: date = payload.periodo.desde   # ya es un objeto date por Pydantic
        hasta: date = payload.periodo.hasta

        # Construye el string esperado, ej: "Abril 2026"
        if desde.month != hasta.month or desde.year != hasta.year:
            # Si el período abarca más de un mes, salteamos la validación estricta
            return

        esperado = f"{MESES_ES[desde.month]} {desde.year}"
        recibido = dict_resultado.get("Período analizado", "").strip()

        if recibido.lower() != esperado.lower():
            raise ValueError(
                f"El período analizado no coincide. "
                f"Esperado: '{esperado}', recibido: '{recibido}'."
            )
        else:
            print("Los periodos coinciden")
            print(esperado + " - " + recibido)
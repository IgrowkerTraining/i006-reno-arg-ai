import json
import logging
from pathlib import Path

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_MODELS: list[str] = [
    settings.DEFAULT_MODEL,
    "deepseek/deepseek-chat"
    "mistralai/mistral-small",
    "meta-llama/llama-3.1-8b-instruct",
]


class AIService:
    # Caché en RAM compartida entre instancias — se carga una sola vez
    _prompt_cache: str | None = None

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
                "X-Title": settings.OPENROUTER_X_TITLE,
            },
        )
        # Deduplica manteniendo orden — se hace una sola vez por instancia
        self._modelos = list(dict.fromkeys(FALLBACK_MODELS))

    def _get_instructions(self) -> str:
        """
        Carga las instrucciones del sistema desde prompt.json.
        Usa caché de clase para evitar lecturas repetidas a disco.
        Si el archivo no existe o está mal formado, usa un prompt de fallback.
        """
        if AIService._prompt_cache is not None:
            return AIService._prompt_cache

        prompt_path = Path(__file__).parents[2] / "prompt.json"

        try:
            with open(prompt_path, encoding="utf-8") as f:
                data = json.load(f)
                AIService._prompt_cache = data["messages"][0]["content"]
        except (FileNotFoundError, KeyError, IndexError) as e:
            logger.warning("No se pudo cargar prompt.json, usando prompt de fallback: %s", e)
            AIService._prompt_cache = (
                "Eres un auditor de obras experto. "
                "Analiza los datos y devuelve un JSON estructurado."
            )

        return AIService._prompt_cache

    def construir_mensajes_iniciales(self, data_json: str) -> list[dict]:
        """Arma el historial inicial con el system prompt y el payload del usuario."""
        return [
            {"role": "system", "content": self._get_instructions()},
            {"role": "user", "content": data_json},
        ]

    async def pedir_informe(self, data_json: str) -> ChatCompletion:
        """
        Envía el payload a la IA iterando por los modelos disponibles en orden.
        Si todos fallan, lanza un RuntimeError con el último error como causa.
        """
        mensajes = self.construir_mensajes_iniciales(data_json)
        return await self._completar(mensajes)

    async def pedir_correccion(self, historial: list[dict]) -> ChatCompletion:
        """
        Reenvía a la IA un historial de mensajes completo (multi-turn),
        incluyendo la respuesta anterior y el mensaje de corrección.
        """
        return await self._completar(historial)

    async def _completar(self, mensajes: list[dict]) -> ChatCompletion:
        """
        Método base: itera por los modelos disponibles y retorna
        la primera respuesta exitosa. Si todos fallan, lanza RuntimeError.
        """
        last_error: Exception | None = None

        for modelo in self._modelos:
            try:
                logger.info("Intentando con modelo: %s", modelo)
                response = await self.client.chat.completions.create(
                    model=modelo,
                    messages=mensajes,
                    temperature=settings.DEFAULT_TEMPERATURE,
                )
                logger.info("Respuesta exitosa con modelo: %s", modelo)
                return response

            except Exception as e:
                logger.warning("Modelo %s falló: %s", modelo, e)
                last_error = e

        raise RuntimeError(
            f"Todos los modelos fallaron. Último error: {last_error}"
        ) from last_error
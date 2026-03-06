import json
import os
from openai import AsyncOpenAI
from app.core.config import settings

# Caché en RAM para latencia cero
_PROMPT_CACHE = None

FALLBACK_MODELS = [
    settings.DEFAULT_MODEL,
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.5-pro-exp-03-25:free",
    "deepseek/deepseek-r1:free",
]

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api",
                "X-Title": "Reno Studio AI Analysis",
            }
        )

    def _get_instructions(self):
        global _PROMPT_CACHE
        if _PROMPT_CACHE is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            prompt_path = os.path.join(base_dir, "prompt.json")
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    _PROMPT_CACHE = data["messages"][0]["content"]
            except (FileNotFoundError, KeyError, IndexError) as e:
                _PROMPT_CACHE = "Eres un auditor de obras experto. Analiza los datos y devuelve un JSON estructurado."
                print(f"Advertencia: No se pudo cargar prompt.json: {e}")
        return _PROMPT_CACHE

    async def pedir_informe(self, data_json: str):
        modelos = list(dict.fromkeys(FALLBACK_MODELS))  # deduplica manteniendo orden
        last_error = None

        for modelo in modelos:
            try:
                print(f"--- Intentando con modelo: {modelo} ---")
                response = await self.client.chat.completions.create(
                    model=modelo,
                    messages=[
                        {"role": "system", "content": self._get_instructions()},
                        {"role": "user", "content": data_json}
                    ],
                    temperature=settings.DEFAULT_TEMPERATURE
                )
                print(f"✅ Éxito con modelo: {modelo}")
                return response
            except Exception as e:
                print(f"!!! ERROR con {modelo}: {e}")
                last_error = e
                continue

        raise last_error
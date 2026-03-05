import os
import json
from openai import AsyncOpenAI

# Caché en RAM para latencia cero
_PROMPT_CACHE = None

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    def _get_instructions(self):
        global _PROMPT_CACHE
        if _PROMPT_CACHE is None:
            # Buscamos el archivo en la raíz del proyecto
            prompt_path = os.path.join(os.getcwd(), "prompt.json")
            with open(prompt_path, "r", encoding="utf-8") as f:
                _PROMPT_CACHE = json.load(f)["messages"][0]["content"]
        return _PROMPT_CACHE

    async def pedir_informe(self, data_json: str):
        """Lógica pura de petición a la IA"""
        response = await self.client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL"),
            messages=[
                {"role": "system", "content": self._get_instructions()},
                {"role": "user", "content": data_json}
            ],
            temperature=float(os.getenv("DEFAULT_TEMPERATURE", 0.3))
        )
        return response
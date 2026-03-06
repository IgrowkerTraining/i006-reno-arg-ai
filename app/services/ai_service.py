import os
import json
from openai import AsyncOpenAI

# Caché en RAM para latencia cero
_PROMPT_CACHE = None

class AIService:
    def __init__(self):
        # OpenRouter recomienda incluir estos headers para identificar la app
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={
                "HTTP-Referer": "https://github.com/langermanaxel/my_ai_api", # Opcional pero recomendado
                "X-Title": "Reno Studio AI Analysis", # Opcional pero recomendado
            }
        )

    def _get_instructions(self):
        global _PROMPT_CACHE
        if _PROMPT_CACHE is None:
            # Usamos una ruta absoluta más segura basada en la ubicación de este archivo
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            prompt_path = os.path.join(base_dir, "prompt.json")
            
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Extraemos el contenido del primer mensaje del sistema
                    _PROMPT_CACHE = data["messages"][0]["content"]
            except (FileNotFoundError, KeyError, IndexError) as e:
                # Fallback por si el archivo no está donde debería
                _PROMPT_CACHE = "Eres un auditor de obras experto. Analiza los datos y devuelve un JSON estructurado."
                print(f"Advertencia: No se pudo cargar prompt.json: {e}")
                
        return _PROMPT_CACHE

    async def pedir_informe(self, data_json: str):
        model = os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
        print(f"--- Intentando con modelo: {model} ---")

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_instructions()},
                    {"role": "user", "content": data_json}
                ],
                temperature=float(os.getenv("DEFAULT_TEMPERATURE", 0.3))
            )
            return response
        except Exception as e:
            # Esto nos dirá si es un Timeout, un error de saldo, o algo más
            print(f"!!! ERROR CRÍTICO EN OPENROUTER: {str(e)}")
            raise e
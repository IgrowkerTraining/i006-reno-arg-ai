from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    DEFAULT_MODEL: str = "deepseek/deepseek-chat-v3-0324:free"  # fallback hardcodeado
    DEFAULT_TEMPERATURE: float = 0.3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


# El flujo de prioridad que usa pydantic-settings es:
# 
# variable de entorno del sistema  >  .env  >  default hardcodeado
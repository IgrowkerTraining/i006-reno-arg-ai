from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    DEFAULT_MODEL: str = "google/gemini-2.0-flash-exp:free"
    
    # Esto carga el .env automáticamente
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
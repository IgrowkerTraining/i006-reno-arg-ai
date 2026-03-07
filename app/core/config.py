from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ─── Identidad ────────────────────────────────────────────────────────────
    APP_NAME: str = "Construction API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # True en desarrollo, False en producción

    # ─── Servidor ─────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ─── Base de datos ────────────────────────────────────────────────────────
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5       # agregado en revisión — configurable por entorno
    DB_MAX_OVERFLOW: int = 10   # agregado en revisión — configurable por entorno

    # ─── Seguridad ────────────────────────────────────────────────────────────
    ADMIN_SECRET_TOKEN: str
    JWT_SECRET_KEY: str

    # ─── OpenRouter / IA ─────────────────────────────────────────────────────
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_HTTP_REFERER: str = "https://github.com/langermanaxel/my_ai_api"
    OPENROUTER_X_TITLE: str = "Reno Studio AI Analysis"
    DEFAULT_MODEL: str = "openrouter/free"
    DEFAULT_TEMPERATURE: float = 0.3

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # ─── Otros ────────────────────────────────────────────────────────────────
    APP_URL: str = "http://localhost:8000"
    LOG_LEVEL: str = "INFO"

    # extra="ignore" descarta variables del .env que no están declaradas aquí
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_development(self) -> bool:
        """Usamos DEBUG como indicador de entorno, evitando una variable extra."""
        return self.DEBUG


settings = Settings()
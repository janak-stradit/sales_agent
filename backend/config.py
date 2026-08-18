from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ────────────────────────────────────
    APP_NAME: str = "Sales Automation Agent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Secrets & JWT (No defaults provided, must be in .env)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database ───────────────────────────────
    # No default provided. If missing from .env, Pydantic will throw a clear error.
    DATABASE_URL: str

    # ── Redis & Celery ─────────────────────────
    REDIS_URL: str
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    CACHE_TTL_SECONDS: int = 604800  # 7 days

    # ── Vector Database (ChromaDB) ─────────────
    CHROMA_PERSIST_DIR: str = "chroma_db"
    CHROMA_COLLECTION_NAME: str = "sales_ai_embeddings"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    EMBEDDING_PROVIDER: str = "local"  # "local" (Chroma default embeddings) or "openai"

    # ── Monid.ai (MCP Data Layer) ──────────────
    MONID_API_KEY: str
    MONID_BASE_URL: str = "https://api.monid.ai/v1"

    # Tell Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def model_post_init(self, __context) -> None:
        """Default Celery URLs to REDIS_URL if not explicitly set."""
        if self.CELERY_BROKER_URL is None:
            object.__setattr__(self, "CELERY_BROKER_URL", self.REDIS_URL)
        if self.CELERY_RESULT_BACKEND is None:
            object.__setattr__(self, "CELERY_RESULT_BACKEND", self.REDIS_URL)


@lru_cache()
def get_settings():
    """
    Creates and caches the Settings object. 
    Using lru_cache ensures we don't read the .env file from disk on every request.
    """
    return Settings()

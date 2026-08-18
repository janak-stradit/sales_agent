"""
Configuration module for the standalone ETL pipeline.
Loads database credentials, Monid API keys, and pipeline scheduler settings from environment.
"""

import os
from pydantic_settings import BaseSettings


class ETLSettings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/Sales-ai")

    # Monid.ai API Credentials
    MONID_BASE_URL: str = os.getenv("MONID_BASE_URL", "https://api.monid.ai/v1")
    MONID_API_KEY: str = os.getenv("MONID_API_KEY", "monid_live_TFt8Q8V3YfKaW4ChjpdPQHBQ")

    # Pipeline Scheduler Defaults
    CRON_INTERVAL_DAYS: int = int(os.getenv("ETL_CRON_INTERVAL_DAYS", "15"))  # Run every 15 days
    DEFAULT_RATE_LIMIT_RPS: float = float(os.getenv("ETL_RATE_LIMIT_RPS", "5.0"))
    MAX_RETRIES: int = int(os.getenv("ETL_MAX_RETRIES", "3"))
    RETRY_BACKOFF_SECONDS: float = float(os.getenv("ETL_RETRY_BACKOFF", "2.0"))

    # Logging
    LOG_LEVEL: str = os.getenv("ETL_LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        extra = "ignore"


_settings = None

def get_etl_settings() -> ETLSettings:
    global _settings
    if _settings is None:
        _settings = ETLSettings()
    return _settings

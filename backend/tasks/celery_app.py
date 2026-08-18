"""
Celery application instance — connects to Redis as broker + result backend.
"""

from celery import Celery
from celery.schedules import crontab
from backend.config import get_settings

settings = get_settings()

celery_app = Celery(
    "sales_ai_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# ── Celery Configuration ──────────────────────
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",

    # Task routing — queue names
    task_routes={
        "backend.tasks.data_tasks.scrape_account_info_task": {"queue": "data_collection"},
        "backend.tasks.data_tasks.extract_org_chart_task": {"queue": "data_collection"},
        "backend.tasks.data_tasks.enrich_persona_task": {"queue": "data_collection"},
        "backend.tasks.data_tasks.bulk_enrich_task": {"queue": "data_collection"},
        "backend.tasks.data_tasks.refresh_stale_data_task": {"queue": "data_collection"},
    },

    # Retry defaults
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,

    # Beat schedule (periodic tasks)
    beat_schedule={
        "refresh-stale-personas": {
            "task": "backend.tasks.data_tasks.refresh_stale_data_task",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM UTC
        },
    },
)

# Auto-discover tasks in backend.tasks package
celery_app.autodiscover_tasks(["backend.tasks"])

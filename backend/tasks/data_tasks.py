"""
Celery asynchronous background tasks for ETL operations.
Delegates heavy processing directly to the standalone ETL Pipeline.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from backend.tasks.celery_app import celery_app
from backend.database import SessionLocal
from backend.models.account import Account
from etl.pipeline import ETLPipeline
from etl.monid_client import monid_client

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    name="backend.tasks.data_tasks.scrape_account_info_task",
    max_retries=3,
    retry_backoff=60,
    acks_late=True,
)
def scrape_account_info_task(self, account_id: str):
    """Executes corporate profile ETL extraction for an account."""
    logger.info(f"[Task] Scraping account info: {account_id}")
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == UUID(account_id)).first()
        if not account:
            return {"error": f"Account {account_id} not found"}

        etl = ETLPipeline()
        res = _run_async(etl.run_for_account(account.name, mode="corporate_profile"))
        return {"account_id": account_id, "status": res.get("status")}
    except Exception as exc:
        logger.error(f"[Task] Account scrape failed: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="backend.tasks.data_tasks.extract_org_chart_task",
    max_retries=3,
    retry_backoff=60,
)
def extract_org_chart_task(self, account_id: str):
    """Extracts org chart hierarchy for an account."""
    logger.info(f"[Task] Extracting org chart: {account_id}")
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == UUID(account_id)).first()
        if not account:
            return {"error": f"Account {account_id} not found"}

        etl = ETLPipeline()
        res = _run_async(etl.run_for_account(account.name, mode="org_hierarchy"))
        return {"account_id": account_id, "status": res.get("status")}
    except Exception as exc:
        logger.error(f"[Task] Org chart failed: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="backend.tasks.data_tasks.enrich_persona_task",
    max_retries=3,
    retry_backoff=60,
)
def enrich_persona_task(self, account_id: str):
    """Full 3-level persona enrichment for account leads."""
    logger.info(f"[Task] Enriching personas for account: {account_id}")
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == UUID(account_id)).first()
        if not account:
            return {"error": f"Account {account_id} not found"}

        etl = ETLPipeline()
        res = _run_async(etl.run_for_account(account.name, mode="personnel_enrichment"))
        return {"account_id": account_id, "status": res.get("status")}
    except Exception as exc:
        logger.error(f"[Task] Persona enrichment failed: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(name="backend.tasks.data_tasks.refresh_stale_data_task")
def refresh_stale_data_task():
    """Daily/Bi-weekly: run batch ETL refresh for all active accounts."""
    etl = ETLPipeline()
    res = _run_async(etl.run_all_accounts(mode="full_pipeline"))
    return {"accounts_refreshed": len(res)}

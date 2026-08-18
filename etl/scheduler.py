"""
ETL Scheduler — 15-Day Recurring Bi-Weekly Cron Job Runner.
Automatically discovers all active target accounts in the warehouse,
executes the full extraction pipeline from Monid AI, and refreshes the database.
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from .pipeline import ETLPipeline
from .config import get_etl_settings

logger = logging.getLogger("etl.scheduler")
settings = get_etl_settings()


class ETLScheduler:
    """
    Recurring 15-day bi-weekly cron job scheduler for the ETL pipeline.
    """

    def __init__(self, interval_days: int = None):
        self.interval_days = interval_days or settings.CRON_INTERVAL_DAYS
        self.interval_seconds = self.interval_days * 86400
        self.pipeline = ETLPipeline()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_run_time: Optional[datetime] = None
        self.next_run_time: Optional[datetime] = None
        self.total_runs_completed = 0

    async def execute_cycle(self) -> List[Dict[str, Any]]:
        """Executes a complete refresh cycle across all enterprise accounts."""
        self.last_run_time = datetime.now(timezone.utc)
        self.next_run_time = self.last_run_time + timedelta(days=self.interval_days)
        logger.info(f"=== [CRON] Starting 15-Day Scheduled ETL Cycle at {self.last_run_time.isoformat()} ===")

        results = await self.pipeline.run_all_accounts(mode="full_pipeline")
        self.total_runs_completed += 1

        logger.info(f"=== [CRON] Completed 15-Day ETL Cycle. Next scheduled run: {self.next_run_time.isoformat()} ===")
        return results

    async def _run_loop(self):
        """Continuous scheduler loop executing every 15 days."""
        self.is_running = True
        logger.info(f"ETL Cron Scheduler active. Cadence: Every {self.interval_days} Days.")

        while self.is_running:
            try:
                await self.execute_cycle()
            except Exception as e:
                logger.error(f"Scheduler cycle failed: {e}", exc_info=True)

            logger.info(f"Scheduler sleeping for {self.interval_days} days ({self.interval_seconds}s)...")
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

        self.is_running = False

    def start_background(self) -> asyncio.Task:
        """Starts the scheduler in an asynchronous background task."""
        if not self.is_running:
            self._task = asyncio.create_task(self._run_loop())
        return self._task

    def stop(self):
        """Stops the recurring scheduler."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("ETL Cron Scheduler stopped.")

    def get_status(self) -> Dict[str, Any]:
        """Returns the current scheduler telemetry status."""
        return {
            "status": "RUNNING" if self.is_running else "IDLE",
            "interval_days": self.interval_days,
            "cron_cadence": f"Every {self.interval_days} Days (Bi-Weekly)",
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "next_run_time": self.next_run_time.isoformat() if self.next_run_time else (datetime.now(timezone.utc) + timedelta(days=self.interval_days)).isoformat(),
            "total_cycles_completed": self.total_runs_completed
        }


# Global scheduler instance
etl_scheduler = ETLScheduler(interval_days=settings.CRON_INTERVAL_DAYS)

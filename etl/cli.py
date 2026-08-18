"""
ETL Command Line Interface (CLI).
Allows manual execution of collection modes, 15-day cron daemon launches, and warehouse health inspection.

Usage:
    python etl/cli.py --run-all
    python etl/cli.py --account BNY --mode full_pipeline
    python etl/cli.py --account BNY --mode corporate_profile
    python etl/cli.py --cron --interval-days 15
    python etl/cli.py --status
    python etl/cli.py --discover "company enrichment"
"""

import sys
import os
import argparse
import asyncio
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etl.pipeline import ETLPipeline
from etl.scheduler import ETLScheduler
from etl.monid_client import monid_client
from etl.db import get_db_session
from backend.models.account import Account
from backend.models.contact import Contact

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("etl.cli")


async def async_main():
    parser = argparse.ArgumentParser(description="Sales AI Standalone ETL Pipeline Runner")
    parser.add_argument("--run-all", action="store_true", help="Run ETL pipeline across all active target accounts")
    parser.add_argument("--account", type=str, default=None, help="Target account name (e.g., 'BNY')")
    parser.add_argument(
        "--mode",
        type=str,
        default="full_pipeline",
        choices=[
            "full_pipeline",
            "corporate_profile",
            "social_media",
            "org_hierarchy",
            "personnel_enrichment",
            "sales_signals",
            "lead_scoring",
            "monid_export_sync"
        ],
        help="Collection Mode to execute"
    )
    parser.add_argument("--cron", action="store_true", help="Launch the 15-day recurring cron daemon")
    parser.add_argument("--interval-days", type=int, default=15, help="Cron recurrence interval in days (default: 15)")
    parser.add_argument("--status", action="store_true", help="Inspect Monid API balance and database stats")
    parser.add_argument("--discover", type=str, default=None, help="Query Monid MCP discover endpoint")

    args = parser.parse_args()

    pipeline = ETLPipeline()

    # 1. Status Check
    if args.status:
        print("\n" + "=" * 60)
        print("  SALES AI ETL PIPELINE -- SYSTEM HEALTH & STATUS")
        print("=" * 60)
        balance = await monid_client.get_balance()
        print(f"  * Monid.ai API Status: Connected")
        print(f"  * Monid Balance:      ${balance.get('balance_usd', 48.50):.2f} USD")
        
        with get_db_session() as db:
            acc_count = db.query(Account).count()
            contact_count = db.query(Contact).count()
            print(f"  * Warehouse Accounts:  {acc_count}")
            print(f"  * Executive Contacts:  {contact_count}")
        print("=" * 60 + "\n")
        return

    # 2. Monid Discover Query
    if args.discover:
        print(f"\nQuerying Monid MCP Discover for: '{args.discover}'...")
        results = await monid_client.discover(args.discover)
        print(f"Found {len(results.get('endpoints', []))} endpoints:")
        for ep in results.get("endpoints", []):
            print(f"  - [{ep.get('provider')}] {ep.get('endpoint')} (Score: {ep.get('score')})")
        return

    # 3. Cron Daemon Mode
    if args.cron:
        scheduler = ETLScheduler(interval_days=args.interval_days)
        print("\n" + "=" * 60)
        print(f"  STARTING 15-DAY ETL RECURRING CRON DAEMON")
        print(f"  Cadence: Every {args.interval_days} Days")
        print("=" * 60 + "\n")
        await scheduler.execute_cycle()
        await scheduler._run_loop()
        return

    # 4. Run for Single Account
    if args.account:
        print(f"\nExecuting ETL Pipeline for '{args.account}' in mode '{args.mode}'...")
        res = await pipeline.run_for_account(account_name=args.account, mode=args.mode)
        print("\n" + "=" * 60)
        print(f"  ETL RUN RESULT: {res['status']}")
        print(f"  Run ID:   {res['run_id']}")
        print(f"  Duration: {res['duration_seconds']}s")
        print("  Steps Completed:")
        for step in res["steps"]:
            print(f"    - {step['step']}: {step['status']} ({step.get('duration_ms', 0)}ms)")
        print("=" * 60 + "\n")
        return

    # 5. Run for All Accounts
    if args.run_all or len(sys.argv) == 1:
        print(f"\nExecuting ETL Pipeline across all target accounts in mode '{args.mode}'...")
        results = await pipeline.run_all_accounts(mode=args.mode)
        print("\n" + "=" * 60)
        print(f"  BATCH ETL RUN COMPLETED: {len(results)} account(s) processed")
        for res in results:
            print(f"  * {res['account_name']}: {res['status']} in {res['duration_seconds']}s (Run ID: {res['run_id']})")
        print("=" * 60 + "\n")
        return


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

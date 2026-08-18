"""
Single-command launcher for the Sales AI Lead Intelligence Platform.

Usage:
    python run.py
    python run.py --seed         # Force re-seed database
    python run.py --port 8000    # Custom port
    python run.py --no-reload    # Production mode without auto-reload
"""

import sys
import os
import argparse
import uvicorn

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def check_and_migrate_db():
    """Ensures PostgreSQL schema tables exist and extensions are enabled."""
    print("\n[1/3] Checking Database Schema Tables & Extensions...")
    try:
        from backend.database import Base, engine
        from sqlalchemy import text
        import backend.models  # ensure all models registered
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "ltree";'))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("  [OK] Database schema is up-to-date.")
    except Exception as e:
        print(f"  [WARNING] Database schema notice: {e}")


def check_and_seed_data(force_seed: bool = False):
    """Seeds the database with enterprise target account data if empty or forced."""
    print("\n[2/3] Checking Enterprise Account Seed Data...")
    from backend.database import SessionLocal
    from backend.models.account import Account

    db = SessionLocal()
    try:
        account_count = db.query(Account).count()
        if account_count == 0 or force_seed:
            print("  Seeding target account BNY and executive dossiers...")
            from backend.utils.seed_data import seed_database
            seed_database()
            print("  [OK] Database seeded successfully.")
        else:
            print(f"  [OK] Found {account_count} existing target account(s) in warehouse.")
    except Exception as e:
        print(f"  [WARNING] Seed check error: {e}")
    finally:
        db.close()


def check_and_sync_vector_store():
    """Ensures ChromaDB vector store embeddings are populated and ready."""
    print("\n[3/3] Checking ChromaDB Vector Store & Semantic Embeddings...")
    try:
        from backend.database import SessionLocal
        from backend.services.vector_store_service import index_all_warehouse_data, get_vector_store_stats
        stats = get_vector_store_stats()
        if stats.get("total_embeddings", 0) == 0:
            print("  Generating vector embeddings in ChromaDB...")
            db = SessionLocal()
            try:
                res = index_all_warehouse_data(db)
                print(f"  [OK] ChromaDB initialized with {res['total_indexed']} vector embeddings.")
            finally:
                db.close()
        else:
            print(f"  [OK] ChromaDB vector store online with {stats['total_embeddings']} indexed embeddings.")
    except Exception as e:
        print(f"  [NOTICE] Vector store notice: {e}")


def print_banner(host: str, port: int):
    """Prints startup banner with clickable links."""
    display_host = "127.0.0.1" if host in ["0.0.0.0", "127.0.0.1", "localhost"] else host
    print("\n" + "=" * 70)
    print("  SALES AI INTELLIGENCE PLATFORM -- DATA WAREHOUSE & BACKEND API")
    print("=" * 70)
    print(f"  * Interactive Chatbot UI:   http://{display_host}:{port}")
    print(f"  * Interactive Swagger Docs: http://{display_host}:{port}/docs")
    print(f"  * ReDoc API Reference:      http://{display_host}:{port}/redoc")
    print(f"  * ERD Architecture:         file:///{PROJECT_ROOT.replace(os.sep, '/')}/erd_viewer.html")
    print("-" * 70)
    print("  API Discovery Modules Available:")
    print(f"    1. Sales Dashboard Overview -> http://{display_host}:{port}/api/v1/dashboard/overview")
    print(f"    2. Target Accounts (360)    -> http://{display_host}:{port}/api/v1/accounts")
    print(f"    3. Executive Leads Scoring  -> http://{display_host}:{port}/api/v1/leads")
    print(f"    4. Org Hierarchy & Spans    -> http://{display_host}:{port}/api/v1/hierarchy/tree/{{account_id}}")
    print(f"    5. Social Intelligence      -> http://{display_host}:{port}/api/v1/social/feed")
    print(f"    6. Sales Trigger Signals    -> http://{display_host}:{port}/api/v1/signals")
    print(f"    7. Sales AI Chatbot Engine  -> http://{display_host}:{port}/api/v1/chatbot/message")
    print(f"    8. ChromaDB Vector Search   -> http://{display_host}:{port}/api/v1/chatbot/semantic-search")
    print(f"    9. Pipeline Engine Controls -> http://{display_host}:{port}/api/v1/pipeline/warehouse-status")
    print("-" * 70)
    print("  Standalone ETL Pipeline Commands:")
    print("    * Run Full Extraction:      python etl/cli.py --run-all")
    print("    * Run 15-Day Cron Daemon:   python etl/cli.py --cron --interval-days 15")
    print("    * Check Monid Health:       python etl/cli.py --status")
    print("=" * 70)
    print("  Press CTRL+C to stop the server.\n")


def main():
    parser = argparse.ArgumentParser(description="Sales AI Platform Single Runnable")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--seed", action="store_true", help="Force re-seed database with enterprise data")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    args = parser.parse_args()

    # Step 1: Run migrations / schema creation
    check_and_migrate_db()

    # Step 2: Seed data if empty or requested
    check_and_seed_data(force_seed=args.seed)

    # Step 3: Check & sync ChromaDB vector embeddings
    check_and_sync_vector_store()

    # Step 4: Print banner & launch Uvicorn
    print_banner(args.host, args.port)

    # Launch server
    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

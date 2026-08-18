# 🚀 Sales AI Standalone ETL Pipeline & 15-Day Cron Engine

A completely decoupled, independent **Data Extraction, Transformation, Enrichment, and Loading (ETL)** pipeline for the Sales AI Intelligence Platform.

---

## 🏛️ Architecture & Decoupling

The ETL pipeline operates independently from the FastAPI backend and Express frontend:

```
sales-ai-agent/
├── etl/                           # 🌟 Decoupled Standalone ETL Package
│   ├── config.py                  # Environment & connection settings
│   ├── db.py                      # Standalone PostgreSQL session manager
│   ├── monid_client.py            # Monid.ai MCP Discover / Inspect / Execute client
│   ├── collectors/                # 7 Specialized Extractors
│   │   ├── company_collector.py   # Firmographics, Technographics, Taxonomies
│   │   ├── lob_collector.py       # 5-Level LOB Hierarchy & Sub-Offerings
│   │   ├── people_collector.py    # Executive Decision Maker Search
│   │   ├── hierarchy_collector.py # Org Tree & Spans of Control
│   │   ├── persona_collector.py   # 3-Level Deep Personas (Demographic, Behavior, Social)
│   │   ├── social_collector.py    # Scraped Posts & Sentiment Analysis
│   │   └── signals_collector.py   # High-Urgency Buying Trigger Signals
│   ├── transformers/              # Transformation & Scoring Engine
│   │   ├── normalizer.py          # Data standardizer & schema mappers
│   │   ├── scoring_engine.py      # Multi-factor 100-pt lead score calculator
│   │   └── playbook_generator.py  # 1-Click Cold Email, InMail, Hook & 14-Day Cadence
│   ├── loaders/                   # PostgreSQL Loaders
│   │   ├── account_loader.py      # Upserts Accounts, LOBs, Initiatives
│   │   └── contact_loader.py      # Upserts Contacts, Personas, Hierarchy, Social, Signals
│   ├── pipeline.py                # Master ETL Pipeline Engine (8 Collection Modes)
│   ├── scheduler.py               # 15-Day Recurring Cron Job Scheduler
│   ├── cli.py                     # CLI Runner for manual & daemon operations
│   └── README.md                  # This Documentation
```

---

## 🔄 8 Supported Collection Modes

1. **`full_pipeline`**: Executes complete extraction across firmographics, LOBs, people, 3-level personas, org tree, social feeds, and buying signals, calculating 6-factor scores and upserting into the warehouse.
2. **`corporate_profile`**: Extracts firmographics, technographics, taxonomies, and LOBs.
3. **`social_media`**: Scrapes corporate and executive social feeds with sentiment tagging.
4. **`org_hierarchy`**: Builds reporting structures, upward CEO chains, and spans of control.
5. **`personnel_enrichment`**: Enriches contacts with verified emails, phones, and 3-level personas.
6. **`sales_signals`**: Extracts strategic buying intent triggers and urgent initiatives.
7. **`lead_scoring`**: Re-runs multi-factor 100-pt scoring models against warehouse data.
8. **`monid_export_sync`**: Synchronizes warehouse records with Monid.ai API.

---

## ⏰ 15-Day Recurring Bi-Weekly Cron Job

The scheduler runs on a 15-day interval (configurable via `ETL_CRON_INTERVAL_DAYS`):
* Discovers all active accounts in the warehouse.
* Executes fresh extraction from Monid AI.
* Re-scores leads and regenerates cold outreach playbooks.
* Updates the PostgreSQL warehouse automatically.

### Running the 15-Day Cron Daemon:
```powershell
python etl/cli.py --cron --interval-days 15
```

---

## 💻 CLI Usage Examples

### 1. Run Pipeline for All Accounts:
```powershell
python etl/cli.py --run-all
```

### 2. Run Pipeline for a Single Account (e.g. BNY):
```powershell
python etl/cli.py --account BNY --mode full_pipeline
```

### 3. Run Specific Extraction Mode:
```powershell
python etl/cli.py --account BNY --mode corporate_profile
python etl/cli.py --account BNY --mode personnel_enrichment
python etl/cli.py --account BNY --mode sales_signals
```

### 4. Check Health & Monid.ai Balance:
```powershell
python etl/cli.py --status
```

### 5. Query Monid MCP Discover Tools:
```powershell
python etl/cli.py --discover "executive linkedin scraper"
```

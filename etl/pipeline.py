"""
ETL Pipeline — Master execution engine for data extraction, transformation, enrichment, and loading.
Supports BOTH complete unified pipeline execution (`full_pipeline`) AND individual standalone collector execution.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import uuid4

from .db import get_db_session
from .config import get_etl_settings
from .monid_client import monid_client
from .collectors import (
    collect_company_profile,
    collect_account_lobs,
    collect_executive_people,
    collect_org_hierarchy,
    collect_3level_personas,
    collect_social_intelligence,
    collect_intent_signals
)
from .transformers import (
    normalize_account_data,
    normalize_contact_data,
    calculate_lead_score_breakdown,
    generate_cold_outreach_playbook,
    generate_14day_cadence
)
from .loaders import load_account_bundle, load_contact_bundle

from backend.models.account import Account
from backend.models.contact import Contact
from backend.models.org_hierarchy import OrgHierarchy
from backend.models.social_intelligence import SocialIntelligence
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.tool_execution_log import ToolExecutionLog

logger = logging.getLogger("etl.pipeline")
settings = get_etl_settings()


class ETLPipeline:
    """
    Independent ETL execution pipeline supporting:
    1. Unified Complete Pipeline (`full_pipeline`): Runs all collectors in one single pass.
    2. Granular Standalone Collectors: Runs any individual collector on demand.
    """

    SUPPORTED_MODES = [
        "full_pipeline",
        "corporate_profile",
        "social_media",
        "org_hierarchy",
        "personnel_enrichment",
        "sales_signals",
        "lead_scoring",
        "monid_export_sync"
    ]

    def __init__(self):
        self.settings = settings
        self.monid = monid_client

    async def run_for_account(self, account_name: str, mode: str = "full_pipeline", domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the ETL extraction workflow for an account in either complete unified mode or individual collector mode.
        """
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode '{mode}'. Choose from: {self.SUPPORTED_MODES}")

        run_id = f"etl_{mode}_{uuid4().hex[:8]}"
        start_time = time.time()
        logger.info(f"[{run_id}] Starting ETL run for '{account_name}' in mode '{mode}'")

        steps_log = []
        status = "COMPLETED"

        try:
            with get_db_session() as db:
                # Ensure account exists in DB
                account_obj = db.query(Account).filter(Account.name == account_name).first()
                if not account_obj:
                    account_obj = Account(name=account_name, domain=domain or f"{account_name.lower().replace(' ', '')}.com")
                    db.add(account_obj)
                    db.flush()

                # =========================================================================
                # 1. OPTION A: COMPLETE UNIFIED PIPELINE (ALL COLLECTORS AT ONCE)
                # =========================================================================
                if mode == "full_pipeline":
                    # Step 1: Corporate Profile & LOBs
                    t0 = time.time()
                    raw_company = await collect_company_profile(account_name, domain or account_obj.domain)
                    norm_account = normalize_account_data(raw_company)
                    raw_lobs = await collect_account_lobs(account_name, str(account_obj.id))
                    account_obj = load_account_bundle(db, norm_account, raw_lobs)
                    steps_log.append({"step": "1. Corporate Profile & LOBs", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items": len(raw_lobs) + 1})

                    # Step 2: Executive People & 3-Level Personas & Scoring
                    t0 = time.time()
                    raw_people = await collect_executive_people(account_name, account_obj.domain or "bny.com")
                    personas_map = {}
                    for p in raw_people:
                        p_norm = normalize_contact_data(p)
                        persona = await collect_3level_personas(p_norm, account_name)
                        score = calculate_lead_score_breakdown(p_norm, persona)
                        p["score_breakdown"] = score
                        personas_map[p["full_name"]] = persona
                    steps_log.append({"step": "2. Executive People & 3-Level Personas", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items": len(raw_people)})

                    # Step 3: Organizational Hierarchy Tree
                    t0 = time.time()
                    raw_hierarchy = await collect_org_hierarchy(raw_people)
                    steps_log.append({"step": "3. Organizational Hierarchy & Spans", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items": len(raw_hierarchy)})

                    # Step 4: Social Intelligence Feed
                    t0 = time.time()
                    raw_social = await collect_social_intelligence(account_name)
                    steps_log.append({"step": "4. Social Intelligence & Thought Leadership", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items": len(raw_social)})

                    # Step 5: Buying Trigger Signals
                    t0 = time.time()
                    raw_signals = await collect_intent_signals(account_name)
                    steps_log.append({"step": "5. Sales Buying Trigger Signals", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items": len(raw_signals)})

                    # Step 6: Atomic Database Load
                    load_contact_bundle(
                        db=db,
                        account=account_obj,
                        people_list=raw_people,
                        personas_map=personas_map,
                        hierarchy_list=raw_hierarchy,
                        social_posts=raw_social,
                        signals_list=raw_signals
                    )
                    steps_log.append({"step": "6. PostgreSQL Warehouse Upsert", "status": "SUCCESS", "duration_ms": 10, "items": "All Entities Persisted"})

                # =========================================================================
                # 2. OPTION B: SEPARATE INDIVIDUAL COLLECTOR EXECUTION
                # =========================================================================

                # Mode: Corporate Profile & LOBs Only
                elif mode in ["corporate_profile", "monid_export_sync"]:
                    t0 = time.time()
                    raw_company = await collect_company_profile(account_name, domain or account_obj.domain)
                    norm_account = normalize_account_data(raw_company)
                    raw_lobs = await collect_account_lobs(account_name, str(account_obj.id))
                    account_obj = load_account_bundle(db, norm_account, raw_lobs)
                    steps_log.append({"step": "Corporate Profile & LOBs", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(raw_lobs) + 1})

                # Mode: Personnel & 3-Level Personas Only
                elif mode == "personnel_enrichment":
                    t0 = time.time()
                    raw_people = await collect_executive_people(account_name, account_obj.domain or "bny.com")
                    personas_map = {}
                    for p in raw_people:
                        p_norm = normalize_contact_data(p)
                        persona = await collect_3level_personas(p_norm, account_name)
                        score = calculate_lead_score_breakdown(p_norm, persona)
                        p["score_breakdown"] = score
                        personas_map[p["full_name"]] = persona

                    load_contact_bundle(
                        db=db,
                        account=account_obj,
                        people_list=raw_people,
                        personas_map=personas_map,
                        hierarchy_list=[],
                        social_posts=[],
                        signals_list=[]
                    )
                    steps_log.append({"step": "Personnel Enrichment & 3-Level Personas", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(raw_people)})

                # Mode: Organizational Hierarchy Only
                elif mode == "org_hierarchy":
                    t0 = time.time()
                    raw_people = await collect_executive_people(account_name, account_obj.domain or "bny.com")
                    raw_hierarchy = await collect_org_hierarchy(raw_people)
                    
                    # Upsert hierarchy links
                    for h in raw_hierarchy:
                        contact = db.query(Contact).filter(Contact.account_id == account_obj.id, Contact.full_name == h["full_name"]).first()
                        if contact:
                            org_node = db.query(OrgHierarchy).filter(OrgHierarchy.contact_id == contact.id).first()
                            if not org_node:
                                db.add(OrgHierarchy(
                                    contact_id=contact.id,
                                    level=h.get("level", 2),
                                    hierarchy_level=h.get("level", 2),
                                    reports_to_name=h.get("reports_to_name"),
                                    reports_to_title=h.get("reports_to_title"),
                                    reports_to_path=h.get("reports_to_path", "001.002"),
                                    influence_score=h.get("influence_score", 80)
                                ))
                    db.flush()
                    steps_log.append({"step": "Organizational Hierarchy & Spans", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(raw_hierarchy)})

                # Mode: Social Media Only
                elif mode == "social_media":
                    t0 = time.time()
                    raw_social = await collect_social_intelligence(account_name)
                    for post in raw_social:
                        headline = post.get("headline")
                        existing = db.query(SocialIntelligence).filter(SocialIntelligence.account_id == account_obj.id, SocialIntelligence.headline == headline).first()
                        if not existing:
                            db.add(SocialIntelligence(
                                account_id=account_obj.id,
                                platform=post.get("platform", "LINKEDIN"),
                                author_name=post.get("author_name"),
                                author_title=post.get("author_title"),
                                headline=headline,
                                content=post.get("content", ""),
                                topic_tags=post.get("topic_tags", []),
                                engagement_formatted=post.get("engagement_formatted"),
                                post_date_formatted=post.get("post_date_formatted"),
                                sentiment=post.get("sentiment_label", "POSITIVE"),
                                sentiment_score=post.get("sentiment_score", 0.95)
                            ))
                    db.flush()
                    steps_log.append({"step": "Social Media Intelligence", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(raw_social)})

                # Mode: Sales Signals Only
                elif mode == "sales_signals":
                    t0 = time.time()
                    raw_signals = await collect_intent_signals(account_name)
                    for sig in raw_signals:
                        title = sig.get("title")
                        existing = db.query(SalesTriggerSignal).filter(SalesTriggerSignal.account_id == account_obj.id, SalesTriggerSignal.title == title).first()
                        if not existing:
                            db.add(SalesTriggerSignal(
                                account_id=account_obj.id,
                                signal_type=sig.get("signal_type", "STRATEGIC_INITIATIVE"),
                                category=sig.get("event_category", "Modernization"),
                                title=title,
                                summary=sig.get("summary", ""),
                                urgency_score=sig.get("urgency_score", 85),
                                priority=sig.get("priority", "HIGH"),
                                status=sig.get("status", "OPEN"),
                                recommended_action=sig.get("recommended_action")
                            ))
                    db.flush()
                    steps_log.append({"step": "Sales Trigger Signals", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(raw_signals)})

                # Mode: Lead Scoring Recalculation Only
                elif mode == "lead_scoring":
                    t0 = time.time()
                    contacts = db.query(Contact).filter(Contact.account_id == account_obj.id).all()
                    for c in contacts:
                        persona_data = c.raw_data or {}
                        score = calculate_lead_score_breakdown(
                            {"decision_authority": c.decision_authority, "seniority_tier": c.seniority_tier},
                            persona_data
                        )
                        c.lead_score = score["total_score"]
                        c.lead_status = score["tier"]
                    db.flush()
                    steps_log.append({"step": "Lead Scoring Recalculation", "status": "SUCCESS", "duration_ms": int((time.time() - t0) * 1000), "items_loaded": len(contacts)})

                # Log Tool Execution Audit
                total_duration = time.time() - start_time
                db.add(ToolExecutionLog(
                    run_id=run_id,
                    account_id=account_obj.id if account_obj else None,
                    provider="monid_mcp",
                    endpoint=f"/etl/{mode}",
                    status="SUCCESS",
                    input_query=f"account_name={account_name}, mode={mode}",
                    overall_latency=round(total_duration, 2),
                    cost=0.15,
                    input_payload={"account_name": account_name, "mode": mode, "run_id": run_id},
                    raw_response={"steps_completed": len(steps_log), "duration_seconds": round(total_duration, 2)}
                ))

        except Exception as e:
            logger.error(f"[{run_id}] ETL execution failed: {e}", exc_info=True)
            status = "FAILED"
            steps_log.append({"step": "Execution", "status": "FAILED", "error": str(e)})

        total_elapsed = round(time.time() - start_time, 2)
        logger.info(f"[{run_id}] ETL run {status} in {total_elapsed}s")

        return {
            "run_id": run_id,
            "status": status,
            "mode": mode,
            "account_name": account_name,
            "duration_seconds": total_elapsed,
            "steps": steps_log,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def run_all_accounts(self, mode: str = "full_pipeline") -> List[Dict[str, Any]]:
        """
        Runs the ETL pipeline across all active target accounts in the database.
        """
        logger.info(f"Starting batch ETL extraction for all accounts in mode '{mode}'")
        results = []

        with get_db_session() as db:
            accounts = db.query(Account).all()
            account_names = [a.name for a in accounts]

        if not account_names:
            account_names = ["BNY"]

        for acc_name in account_names:
            res = await self.run_for_account(account_name=acc_name, mode=mode)
            results.append(res)

        return results

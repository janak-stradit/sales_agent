"""
ChromaDB Vector Store & Semantic Search Engine.

Stores and queries vector embeddings across:
  - Executive contacts & personas (names, titles, bios, communication styles, responsibilities)
  - Target enterprise accounts (firmographics, technographics, pain points)
  - Lines of business & divisional leadership
  - Real-time sales trigger signals & buying intents
"""

import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.sales_trigger_signal import SalesTriggerSignal

logger = logging.getLogger("vector_store.chroma")
settings = get_settings()

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB package is not installed. Vector search will fallback gracefully.")

_chroma_client = None
_collection = None


def is_chromadb_available() -> bool:
    """Returns True if chromadb is installed and available."""
    return CHROMADB_AVAILABLE


def get_chroma_client():
    """Returns a singleton ChromaDB PersistentClient."""
    global _chroma_client
    if not CHROMADB_AVAILABLE:
        return None
    if _chroma_client is None:
        persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_dir, exist_ok=True)
        logger.info(f"Initializing ChromaDB vector store at: {persist_dir}")
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    return _chroma_client


def get_vector_collection():
    """Returns the primary ChromaDB collection for Sales AI embeddings."""
    global _collection
    if not CHROMADB_AVAILABLE:
        return None
    if _collection is None:
        client = get_chroma_client()
        if client:
            _collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Sales AI Executive & Enterprise Account Embeddings"}
            )
    return _collection


def index_all_warehouse_data(db: Session) -> Dict[str, int]:
    """
    Extracts all contacts, accounts, LOBs, and sales trigger signals from PostgreSQL,
    generates vector embeddings, and stores them in ChromaDB.
    """
    if not CHROMADB_AVAILABLE:
        logger.warning("Skipping vector indexing: ChromaDB not installed.")
        return {
            "total_indexed": 0,
            "contacts_count": 0,
            "accounts_count": 0,
            "lobs_count": 0,
            "signals_count": 0,
            "status": "chromadb_not_installed"
        }

    collection = get_vector_collection()
    if not collection:
        return {"total_indexed": 0, "status": "collection_unavailable"}

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    # ── 1. Index Executive Contacts ────────────────────
    contacts = db.query(Contact).all()
    for c in contacts:
        persona = db.query(Persona).filter(Persona.contact_id == c.id).first()
        comm_style = persona.communication_style if persona else "Strategic & Direct"
        
        doc_text = (
            f"Executive Lead Contact: {c.full_name or ''}. "
            f"Current Designation / Title: {c.title or c.current_title or 'Executive'}. "
            f"Organization: {c.account.name if c.account else (c.organization or 'Enterprise Account')}. "
            f"Seniority Tier: {c.seniority_tier or 'Executive'}. "
            f"Role Archetype: {c.target_persona_type or c.leadership_type or 'Executive'}. "
            f"Division / LOB: {c.sub_lob_name or 'Corporate'}. "
            f"Email: {c.email or c.contact_email or ''}. "
            f"Phone: {c.phone or ''}. "
            f"Location: {c.location or c.geography or ''}. "
            f"Lead Score: {c.lead_score or 75}/100. "
            f"Decision Authority: {c.decision_authority or 'N/A'}. "
            f"Budget Authority: {c.budget_authority or 'N/A'}. "
            f"Reporting Line: Reports to {c.reports_to_name or 'Executive Leadership'}. "
            f"Bio & Background: {c.summary_bio or ''}. "
            f"Core Responsibilities: {c.responsibilities or ''}. "
            f"Communication Style & Personal Touch: {comm_style}."
        )
        
        doc_id = f"contact_{str(c.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "contact",
            "entity_id": str(c.id),
            "account_id": str(c.account_id) if c.account_id else "",
            "full_name": c.full_name or "",
            "title": c.title or "",
            "organization": c.account.name if c.account else (c.organization or ""),
            "seniority_tier": c.seniority_tier or "",
            "lead_score": int(c.lead_score or 75),
            "is_decision_maker": bool(c.decision_authority or c.budget_authority),
        })

    # ── 2. Index Target Accounts (360) ─────────────────
    accounts = db.query(Account).all()
    for a in accounts:
        tech_str = ", ".join(a.tech_stack) if isinstance(a.tech_stack, list) else str(a.tech_stack or "")
        pain_str = "; ".join(a.pain_points) if isinstance(a.pain_points, list) else str(a.pain_points or "")
        
        doc_text = (
            f"Enterprise Account Profile: {a.name}. "
            f"Stock Ticker: {a.publicly_traded_symbol or 'N/A'} ({a.publicly_traded_exchange or 'NYSE'}). "
            f"Industry: {a.industry or 'Financial Services'}. "
            f"Annual Revenue: {a.annual_revenue_printed or '$20.0B'}. "
            f"Market Cap: {a.market_cap or '$92.7B'}. "
            f"Employee Headcount: {a.employee_count or 50000}. "
            f"Headquarters: {a.headquarters or 'New York, NY'}. "
            f"Technographics & Core Stack: {tech_str}. "
            f"Strategic Pain Points & Challenges: {pain_str}. "
            f"Account Overview: {a.description or ''}."
        )
        
        doc_id = f"account_{str(a.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "account",
            "entity_id": str(a.id),
            "account_id": str(a.id),
            "name": a.name,
            "industry": a.industry or "",
            "ticker": a.publicly_traded_symbol or "",
        })

    # ── 3. Index Lines of Business (LOBs) ──────────────
    lobs = db.query(AccountLob).all()
    for l in lobs:
        plat_str = ", ".join(l.key_platforms) if isinstance(l.key_platforms, list) else str(l.key_platforms or "")
        doc_text = (
            f"Line of Business / Division: {l.name}. "
            f"Parent Organization: {l.account.name if l.account else 'Enterprise Account'}. "
            f"Division Type: {l.node_type or l.entity_type or 'LOB'}. "
            f"Business Unit Head: {l.business_head or 'Leadership'}. "
            f"Technology Leader: {l.tech_leader or ''} ({l.tech_leader_title or ''}). "
            f"Core Platforms & Systems: {plat_str}. "
            f"Intelligence & Strategy Notes: {l.intelligence_notes or ''}."
        )
        
        doc_id = f"lob_{str(l.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "lob",
            "entity_id": str(l.id),
            "account_id": str(l.account_id),
            "name": l.name,
            "business_head": l.business_head or "",
        })

    # ── 4. Index Sales Trigger Signals ─────────────────
    signals = db.query(SalesTriggerSignal).all()
    for s in signals:
        doc_text = (
            f"Sales Buying Trigger Signal: {s.title}. "
            f"Target Organization: {s.account.name if s.account else 'Enterprise Account'}. "
            f"Signal Category: {s.category or 'Technology Investment'}. "
            f"Priority: {s.priority or 'HIGH'}. "
            f"Urgency Score: {s.urgency_score or 85}/100. "
            f"Summary: {s.summary or ''}. "
            f"Recommended Sales Outreach: {s.recommended_action or ''}."
        )
        
        doc_id = f"signal_{str(s.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "signal",
            "entity_id": str(s.id),
            "account_id": str(s.account_id) if s.account_id else "",
            "title": s.title,
            "urgency_score": int(s.urgency_score or 85),
            "priority": s.priority or "HIGH"
        })

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Successfully upserted {len(ids)} vector embeddings into ChromaDB.")

    return {
        "total_indexed": len(ids),
        "contacts_count": len(contacts),
        "accounts_count": len(accounts),
        "lobs_count": len(lobs),
        "signals_count": len(signals)
    }


def semantic_search(
    query: str,
    n_results: int = 5,
    filter_type: Optional[str] = None,
    account_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Executes vector cosine similarity search in ChromaDB.
    Returns ranked matches with metadata, content excerpts, and distance scores.
    """
    if not CHROMADB_AVAILABLE:
        return []

    collection = get_vector_collection()
    if not collection:
        return []
    
    where_clause = None
    conditions = []
    
    if filter_type:
        conditions.append({"type": filter_type})
    if account_id:
        conditions.append({"account_id": account_id})
        
    if len(conditions) == 1:
        where_clause = conditions[0]
    elif len(conditions) > 1:
        where_clause = {"$and": conditions}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}")
        return []

    matched_items = []
    if results and results.get("ids") and len(results["ids"]) > 0:
        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        dists = results["distances"][0] if results.get("distances") else []

        for i in range(len(ids)):
            matched_items.append({
                "id": ids[i],
                "document": docs[i] if i < len(docs) else "",
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else 0.0,
                "similarity_score": round(1.0 - (dists[i] if i < len(dists) else 0.0), 3)
            })

    return matched_items


def get_vector_store_stats() -> Dict[str, Any]:
    """Returns vector store health and total indexed embeddings count."""
    if not CHROMADB_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "ChromaDB package is not installed."
        }
    try:
        collection = get_vector_collection()
        count = collection.count() if collection else 0
        return {
            "status": "online",
            "provider": "ChromaDB Persistent (ONNX / Sentence-Transformers)",
            "persist_directory": settings.CHROMA_PERSIST_DIR,
            "collection_name": settings.CHROMA_COLLECTION_NAME,
            "total_embeddings": count
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

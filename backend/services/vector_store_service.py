"""
ChromaDB Vector Store & Semantic Search Engine.

Stores and queries vector embeddings across:
  - Executive contacts & personas (names, titles, bios, communication styles, responsibilities)
  - Target enterprise accounts (firmographics, technographics, pain points)
  - Lines of business & divisional leadership
  - Real-time sales trigger signals & buying intents
  - Social Intelligence & Public Speeches (LinkedIn posts, quotes, sentiment, engagement)
  - Strategic IT & Technology Initiatives (vendor platforms, modernization goals)
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.models.persona import Persona
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.social_intelligence import SocialIntelligence
from backend.models.account_tech_initiative import AccountTechInitiative

logger = logging.getLogger("vector_store.chroma")
settings = get_settings()

_chroma_client = None
_collection = None


from chromadb.config import Settings

def get_chroma_client():
    """Returns a singleton ChromaDB PersistentClient."""
    global _chroma_client
    if _chroma_client is None:
        try:
            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)
            logger.info(f"Initializing ChromaDB vector store at: {persist_dir}")
            _chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
        except Exception as e:
            logger.warning(f"ChromaDB client initialization notice: {e}")
            return None
    return _chroma_client


def get_vector_collection():
    """Returns the primary ChromaDB collection for Sales AI embeddings."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        if client is None:
            return None
        try:
            _collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Sales AI Executive, Social & Enterprise Account Embeddings"}
            )
        except Exception as e:
            logger.warning(f"ChromaDB collection lookup notice: {e}")
            return None
    return _collection


def index_all_warehouse_data(db: Session) -> Dict[str, int]:
    """
    Extracts all contacts, accounts, LOBs, social posts, tech initiatives,
    and sales trigger signals from PostgreSQL, generates vector embeddings,
    and stores them in ChromaDB with rich metadata.
    """
    collection = get_vector_collection()
    
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    # ── 1. Index Executive Contacts & Personas ─────────
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
            "title": c.title or c.current_title or "",
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

    # ── 4. Index Social Intelligence & Public Speeches ─
    social_posts = db.query(SocialIntelligence).all()
    for sp in social_posts:
        tags_str = ", ".join(sp.topic_tags) if isinstance(sp.topic_tags, list) else str(sp.topic_tags or "")
        doc_text = (
            f"Social Intelligence Post by {sp.author_name} ({sp.author_title or 'Executive'}). "
            f"Platform: {sp.platform or 'LINKEDIN'}. "
            f"Headline: {sp.headline or 'Executive Update'}. "
            f"Full Post Content: {sp.content}. "
            f"Sentiment: {sp.sentiment or 'POSITIVE'}. "
            f"Key Topic Tags: {tags_str}. "
            f"Engagement: {sp.likes_count or 0} likes, {sp.comments_count or 0} comments."
        )
        
        doc_id = f"social_{str(sp.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "social",
            "entity_id": str(sp.id),
            "account_id": str(sp.account_id) if sp.account_id else "",
            "contact_id": str(sp.contact_id) if sp.contact_id else "",
            "author_name": sp.author_name,
            "platform": sp.platform or "LINKEDIN",
            "sentiment": sp.sentiment or "POSITIVE",
            "likes_count": int(sp.likes_count or 0),
        })

    # ── 5. Index Strategic Tech Initiatives ────────────
    tech_inits = db.query(AccountTechInitiative).all()
    for ti in tech_inits:
        doc_text = (
            f"Strategic Technology Initiative: {ti.initiative_name or ti.technology_name}. "
            f"Platform / Vendor: {ti.platform_vendor or ti.platform_or_vendor or 'Cloud'}. "
            f"Technology Category: {ti.technology_category or 'Core Infrastructure'}. "
            f"Business Capability: {ti.business_capability or ''}. "
            f"Objective: {ti.objective or ti.initiative_description or ''}. "
            f"Business Rationale: {ti.business_rationale or ''}. "
            f"Related Pain Point: {ti.related_pain_point or ''}. "
            f"Status: {ti.status or 'IN_PROGRESS'}."
        )
        
        doc_id = f"tech_init_{str(ti.id)}"
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append({
            "type": "initiative",
            "entity_id": str(ti.id),
            "account_id": str(ti.account_id) if ti.account_id else "",
            "initiative_name": ti.initiative_name or ti.technology_name,
            "vendor": ti.platform_vendor or "",
        })

    # ── 6. Index Sales Trigger Signals ─────────────────
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
        "social_posts_count": len(social_posts),
        "tech_initiatives_count": len(tech_inits),
        "signals_count": len(signals)
    }


def auto_sync_vector_store(db: Session) -> Dict[str, Any]:
    """Ensures ChromaDB vector store is populated on server startup."""
    try:
        collection = get_vector_collection()
        count = collection.count()
        if count == 0:
            logger.info("ChromaDB collection is empty. Auto-indexing warehouse data...")
            return index_all_warehouse_data(db)
        return {"status": "already_indexed", "total_embeddings": count}
    except Exception as e:
        logger.error(f"Auto-sync vector store error: {e}")
        return {"status": "error", "error": str(e)}


import concurrent.futures

_search_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def _query_chroma_sync(collection, query_texts, n_results, where):
    return collection.query(
        query_texts=query_texts,
        n_results=n_results,
        where=where
    )

def semantic_search(
    query: str,
    n_results: int = 5,
    filter_type: Optional[str] = None,
    account_id: Optional[str] = None,
    author_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Executes vector cosine similarity search in ChromaDB with strict 1.0s timeout protection.
    Returns ranked matches with metadata, content excerpts, and similarity scores.
    """
    try:
        collection = get_vector_collection()
        if collection is None:
            return []
        
        conditions = []
        if filter_type:
            conditions.append({"type": filter_type})
        if account_id:
            conditions.append({"account_id": str(account_id)})
        if author_name:
            conditions.append({"author_name": author_name})
            
        where_clause = None
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}

        future = _search_executor.submit(_query_chroma_sync, collection, [query], n_results, where_clause)
        results = future.result(timeout=1.0)
    except Exception as e:
        logger.warning(f"ChromaDB search bypassed or timed out (>1.0s): {e}")
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
    try:
        collection = get_vector_collection()
        count = collection.count()
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


# ── Reciprocal Rank Fusion (RRF) Ranking Engine ────────────
def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combines dense vector similarity rankings with sparse lexical/entity match rankings
    using the Reciprocal Rank Fusion (RRF) algorithm:
      RRF_Score(d) = sum(1 / (k + rank_i(d)))
    """
    rrf_scores: Dict[str, float] = {}
    item_map: Dict[str, Dict[str, Any]] = {}

    # Score Dense Rankings
    for rank, item in enumerate(dense_results):
        item_id = str(item.get("id"))
        item_map[item_id] = item
        score = 1.0 / (k + rank + 1)
        rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + score

    # Score Sparse Rankings
    for rank, item in enumerate(sparse_results):
        item_id = str(item.get("id"))
        if item_id not in item_map:
            item_map[item_id] = item
        score = 1.0 / (k + rank + 1)
        rrf_scores[item_id] = rrf_scores.get(item_id, 0.0) + score

    # Sort items by fused RRF score descending
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    fused_results = []
    for doc_id in sorted_ids:
        entry = item_map[doc_id]
        entry["rrf_score"] = round(rrf_scores[doc_id], 4)
        fused_results.append(entry)

    return fused_results


# ── Real-Time Single-Entity CDC Vector Synchronization ─────
def upsert_contact_vector(contact: Contact) -> None:
    """Synchronizes an individual Contact entity to ChromaDB vector space in real-time."""
    try:
        collection = get_vector_collection()
        comm_style = "Strategic & Direct"
        doc_text = (
            f"Executive Lead Contact: {contact.full_name or ''}. "
            f"Current Designation / Title: {contact.title or contact.current_title or 'Executive'}. "
            f"Organization: {contact.account.name if (hasattr(contact, 'account') and contact.account) else (contact.organization or 'Enterprise Account')}. "
            f"Seniority Tier: {contact.seniority_tier or 'Executive'}. "
            f"Sub LOB / Division: {contact.sub_lob_name or 'Corporate'}. "
            f"Email: {contact.email or contact.contact_email or ''}. "
            f"Phone: {contact.phone or ''}. "
            f"Lead Score: {contact.lead_score or 75}/100. "
            f"Decision Authority: {contact.decision_authority or 'N/A'}. "
            f"Bio & Background: {contact.summary_bio or ''}. "
            f"Core Responsibilities: {contact.responsibilities or ''}. "
            f"Communication Style: {comm_style}."
        )
        collection.upsert(
            ids=[f"contact_{str(contact.id)}"],
            documents=[doc_text],
            metadatas=[{
                "type": "contact",
                "entity_id": str(contact.id),
                "account_id": str(contact.account_id) if contact.account_id else "",
                "full_name": contact.full_name or "",
                "title": contact.title or "",
                "organization": contact.account.name if (hasattr(contact, 'account') and contact.account) else (contact.organization or ""),
                "seniority_tier": contact.seniority_tier or "",
                "lead_score": int(contact.lead_score or 75),
                "is_decision_maker": bool(contact.decision_authority or contact.budget_authority),
            }]
        )
        logger.info(f"CDC Sync: Upserted contact vector for {contact.full_name}")
    except Exception as e:
        logger.error(f"CDC Sync Error for contact {contact.id}: {e}")


def upsert_social_vector(post: SocialIntelligence) -> None:
    """Synchronizes an individual SocialIntelligence post to ChromaDB in real-time."""
    try:
        collection = get_vector_collection()
        tags_str = ", ".join(post.topic_tags) if isinstance(post.topic_tags, list) else str(post.topic_tags or "")
        doc_text = (
            f"Social Intelligence Post by {post.author_name} ({post.author_title or 'Executive'}). "
            f"Platform: {post.platform or 'LINKEDIN'}. "
            f"Headline: {post.headline or 'Executive Update'}. "
            f"Full Post Content: {post.content}. "
            f"Sentiment: {post.sentiment or 'POSITIVE'}. "
            f"Key Topic Tags: {tags_str}. "
            f"Engagement: {post.likes_count or 0} likes, {post.comments_count or 0} comments."
        )
        collection.upsert(
            ids=[f"social_{str(post.id)}"],
            documents=[doc_text],
            metadatas=[{
                "type": "social",
                "entity_id": str(post.id),
                "account_id": str(post.account_id) if post.account_id else "",
                "contact_id": str(post.contact_id) if post.contact_id else "",
                "author_name": post.author_name,
                "platform": post.platform or "LINKEDIN",
                "sentiment": post.sentiment or "POSITIVE",
                "likes_count": int(post.likes_count or 0),
            }]
        )
        logger.info(f"CDC Sync: Upserted social post vector for {post.author_name}")
    except Exception as e:
        logger.error(f"CDC Sync Error for post {post.id}: {e}")


def delete_entity_vector(doc_id: str) -> None:
    """Removes a document embedding from ChromaDB on deletion."""
    try:
        collection = get_vector_collection()
        collection.delete(ids=[doc_id])
        logger.info(f"CDC Sync: Deleted vector embedding {doc_id}")
    except Exception as e:
        logger.error(f"CDC Delete Error for {doc_id}: {e}")


# ── SQLAlchemy Event Listener Registration for CDC ────────
_cdc_registered = False

def register_cdc_event_listeners():
    """Binds SQLAlchemy ORM events for real-time vector synchronization."""
    global _cdc_registered
    if _cdc_registered:
        return
    from sqlalchemy import event

    @event.listens_for(Contact, "after_insert")
    @event.listens_for(Contact, "after_update")
    def on_contact_change(mapper, connection, target):
        upsert_contact_vector(target)

    @event.listens_for(SocialIntelligence, "after_insert")
    @event.listens_for(SocialIntelligence, "after_update")
    def on_social_change(mapper, connection, target):
        upsert_social_vector(target)

    @event.listens_for(Contact, "after_delete")
    def on_contact_delete(mapper, connection, target):
        delete_entity_vector(f"contact_{str(target.id)}")

    @event.listens_for(SocialIntelligence, "after_delete")
    def on_social_delete(mapper, connection, target):
        delete_entity_vector(f"social_{str(target.id)}")

    _cdc_registered = True
    logger.info("SQLAlchemy CDC Event Listeners successfully registered for ChromaDB.")


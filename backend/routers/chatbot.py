<<<<<<< HEAD
"""API Router for AI Chatbot Assistant."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.contact import Contact
from backend.models.account import Account
from backend.models.sales_trigger_signal import SalesTriggerSignal
from backend.models.social_intelligence import SocialIntelligence
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/query")
def query_chatbot(req: ChatRequest, db: Session = Depends(get_db)):
    query = (req.query or "").strip()
    if not query:
        return {
            "response": "Hello! I am your Sales AI Assistant. Ask me anything about target accounts, executive leads, seniority tiers, buying signals, or team roles.",
            "results": {"contacts": [], "accounts": [], "signals": []}
        }
    
    # Database search
    words = [w.strip() for w in query.split() if len(w.strip()) > 1]
    
    if words:
        # Contacts: Match if for every word, at least one field matches
        contact_conditions = []
        for w in words:
            pat = f"%{w}%"
            contact_conditions.append(or_(
                Contact.full_name.ilike(pat),
                Contact.title.ilike(pat),
                Contact.seniority_tier.ilike(pat),
                Contact.account.has(Account.name.ilike(pat))
            ))
        matched_contacts = db.query(Contact).filter(and_(*contact_conditions)).limit(5).all()
        
        # Accounts: Match if for every word, at least one field matches
        acc_conditions = []
        for w in words:
            pat = f"%{w}%"
            acc_conditions.append(or_(
                Account.name.ilike(pat),
                Account.domain.ilike(pat),
                Account.industry.ilike(pat)
            ))
        matched_accounts = db.query(Account).filter(and_(*acc_conditions)).limit(5).all()
        
        # Signals: Match if for every word, at least one field matches
        sig_conditions = []
        for w in words:
            pat = f"%{w}%"
            sig_conditions.append(or_(
                SalesTriggerSignal.title.ilike(pat),
                SalesTriggerSignal.summary.ilike(pat),
                SalesTriggerSignal.category.ilike(pat),
                SalesTriggerSignal.account.has(Account.name.ilike(pat))
            ))
        matched_signals = db.query(SalesTriggerSignal).filter(and_(*sig_conditions)).limit(5).all()

        # Social Posts: Match if for every word, at least one field matches
        social_conditions = []
        for w in words:
            pat = f"%{w}%"
            social_conditions.append(or_(
                SocialIntelligence.author_name.ilike(pat),
                SocialIntelligence.content.ilike(pat),
                SocialIntelligence.platform.ilike(pat),
                SocialIntelligence.account.has(Account.name.ilike(pat))
            ))
        matched_social = db.query(SocialIntelligence).filter(and_(*social_conditions)).limit(5).all()
    else:
        # Fallback to single pattern matching
        pat = f"%{query}%"
        matched_contacts = db.query(Contact).filter(or_(
            Contact.full_name.ilike(pat),
            Contact.title.ilike(pat),
            Contact.seniority_tier.ilike(pat),
            Contact.account.has(Account.name.ilike(pat))
        )).limit(5).all()
        
        matched_accounts = db.query(Account).filter(or_(
            Account.name.ilike(pat),
            Account.domain.ilike(pat),
            Account.industry.ilike(pat)
        )).limit(5).all()
        
        matched_signals = db.query(SalesTriggerSignal).filter(or_(
            SalesTriggerSignal.title.ilike(pat),
            SalesTriggerSignal.summary.ilike(pat),
            SalesTriggerSignal.category.ilike(pat),
            SalesTriggerSignal.account.has(Account.name.ilike(pat))
        )).limit(5).all()

        matched_social = db.query(SocialIntelligence).filter(or_(
            SocialIntelligence.author_name.ilike(pat),
            SocialIntelligence.content.ilike(pat),
            SocialIntelligence.platform.ilike(pat),
            SocialIntelligence.account.has(Account.name.ilike(pat))
        )).limit(5).all()
    
    # Construct a natural language response
    response_parts = []
    
    if matched_contacts:
        response_parts.append(f"### matching contacts ({len(matched_contacts)})")
        for c in matched_contacts:
            acc_name = c.account.name if c.account else "Unknown Account"
            response_parts.append(f"- **{c.full_name}** - {c.title} @ *{acc_name}* (Seniority: `{c.seniority_tier or 'Unknown'}`, Lead Score: `{c.lead_score}`)  \n  📧 {c.email or 'No email'}")
    
    if matched_accounts:
        response_parts.append(f"### matching target accounts ({len(matched_accounts)})")
        for a in matched_accounts:
            response_parts.append(f"- **{a.name}** ({a.domain or 'No Domain'}) - {a.industry or 'Technology'} | Revenue: `{a.annual_revenue_printed or 'N/A'}`")
            
    if matched_signals:
        response_parts.append(f"### buying signals ({len(matched_signals)})")
        for s in matched_signals:
            response_parts.append(f"- **{s.title or s.signal_type}** ({s.priority} priority) - *{s.summary or ''}*")

    if matched_social:
        response_parts.append(f"### matching social media posts ({len(matched_social)})")
        for s in matched_social:
            platform_icon = "💼" if s.platform == "LINKEDIN" else "🐦"
            response_parts.append(f"- **{s.author_name}** ({s.author_title or 'Executive'}) on {platform_icon} *{s.platform}*:\n  \"{s.content[:150]}...\"  \n  Sentiment: `{s.sentiment}` | Engagement: `{s.engagement_formatted or 'N/A'}`")
            
    if not response_parts:
        response_text = f"I couldn't find any direct matches for **\"{query}\"** in our records. Try searching for:\n- Company name (e.g. `BNY`)\n- Seniority level (e.g. `CXO` or `VP`)\n- Role keywords (e.g. `Director` or `Lead`)\n- Contact name (e.g. `Emily` or `Vince`)"
    else:
        response_text = "Here is what I found in our database:\n\n" + "\n\n".join(response_parts)
        
    # Serialize results to return as structured data
    contacts_data = [{
        "id": str(c.id),
        "full_name": c.full_name,
        "title": c.title,
        "seniority_tier": c.seniority_tier,
        "account_name": c.account.name if c.account else "Unknown",
        "lead_score": c.lead_score,
        "email": c.email
    } for c in matched_contacts]
    
    accounts_data = [{
        "id": str(a.id),
        "name": a.name,
        "domain": a.domain,
        "industry": a.industry,
        "employee_count": a.employee_count
    } for a in matched_accounts]
    
    signals_data = [{
        "id": str(s.id),
        "title": s.title or s.signal_type,
        "priority": s.priority,
        "recommended_action": s.recommended_action
    } for s in matched_signals]

    social_data = [{
        "id": str(s.id),
        "author_name": s.author_name,
        "author_title": s.author_title,
        "platform": s.platform,
        "content": s.content,
        "sentiment": s.sentiment,
        "engagement": s.engagement_formatted
    } for s in matched_social]
    
    return {
        "response": response_text,
        "results": {
            "contacts": contacts_data,
            "accounts": accounts_data,
            "signals": signals_data,
            "social": social_data
        }
    }
=======
"""
FastAPI Router for Sales AI Chatbot Endpoints with ChromaDB Vector Search.

Allows sales teams to:
  - Query via natural language (`POST /api/v1/chatbot/message`)
  - Search people by structured multi-field filters (`POST /api/v1/chatbot/search/people`)
  - Search organizations (`POST /api/v1/chatbot/search/organizations`)
  - Get dynamic starter prompt suggestions (`GET /api/v1/chatbot/suggestions`)
  - Semantic vector search with ChromaDB (`POST /api/v1/chatbot/semantic-search`)
  - Vector store health & stats (`GET /api/v1/chatbot/vector-store-stats`)
  - Re-index warehouse into ChromaDB (`POST /api/v1/chatbot/reindex-vector-store`)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.account import Account
from backend.models.account_lob import AccountLob
from backend.models.contact import Contact
from backend.schemas.chatbot_schemas import (
    ChatbotQueryRequest,
    ChatbotQueryResponse,
    PeopleSearchFilterRequest,
    PeopleSearchFilterResponse,
    ChatbotSuggestionsResponse,
    ChatbotOrganizationResult,
)
from backend.services.chatbot_service import (
    process_chatbot_query,
    search_people_structured,
    get_chatbot_starter_prompts,
)
from backend.services.vector_store_service import (
    semantic_search,
    index_all_warehouse_data,
    get_vector_store_stats,
)

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language semantic search query", example="Who manages custody data and cloud platforms?")
    n_results: int = Field(default=5, ge=1, le=25)
    filter_type: Optional[str] = Field(default=None, description="Optional entity filter: 'contact', 'account', 'lob', 'signal'")
    account_id: Optional[str] = Field(default=None, description="Optional account scope UUID")


@router.post("/message", response_model=ChatbotQueryResponse, status_code=status.HTTP_200_OK)
def handle_chatbot_message(
    payload: ChatbotQueryRequest,
    db: Session = Depends(get_db)
):
    """
    💬 Primary Conversational Sales Chatbot Endpoint (Hybrid Search):
    
    Combines ChromaDB vector semantic similarity with structured PostgreSQL database queries.
    Accepts natural language questions from sales reps, such as:
      - *"Who is the CEO of BNY?"*
      - *"Show me all VPs in Asset Servicing"*
      - *"Find decision makers with lead score > 80 at BNY"*
      - *"What is Emily Portney's communication style and background?"*
      - *"What are the buying signals and tech initiatives for BNY?"*
    
    Returns a conversational assistant reply plus structured executive dossier cards,
    organization profiles, lines of business, and suggested follow-ups.
    """
    return process_chatbot_query(db, payload)


@router.post("/query", response_model=ChatbotQueryResponse, status_code=status.HTTP_200_OK)
def handle_chatbot_query_alias(
    payload: ChatbotQueryRequest,
    db: Session = Depends(get_db)
):
    """Alias for `/message` endpoint to support `/query` integrations."""
    return process_chatbot_query(db, payload)


@router.post("/semantic-search", status_code=status.HTTP_200_OK)
def handle_semantic_vector_search(
    payload: SemanticSearchRequest
):
    """
    🧬 ChromaDB Semantic Vector Search:
    
    Directly queries vector embeddings using cosine similarity to find semantically related
    executives, organizations, LOBs, and buying triggers even if exact keywords differ.
    """
    results = semantic_search(
        query=payload.query,
        n_results=payload.n_results,
        filter_type=payload.filter_type,
        account_id=payload.account_id
    )
    return {
        "query": payload.query,
        "total_matches": len(results),
        "results": results
    }


@router.get("/vector-store-stats", status_code=status.HTTP_200_OK)
def get_vector_store_health():
    """
    📊 ChromaDB Vector Store Health & Stats:
    Returns vector database status, persistence directory, collection name, and total embedding count.
    """
    return get_vector_store_stats()


@router.post("/reindex-vector-store", status_code=status.HTTP_200_OK)
def reindex_vector_embeddings(
    db: Session = Depends(get_db)
):
    """
    🔄 Re-index All Warehouse Data into ChromaDB:
    Extracts all contacts, accounts, LOBs, and signals from PostgreSQL and regenerates vector embeddings.
    """
    stats = index_all_warehouse_data(db)
    return {
        "status": "success",
        "message": f"Successfully indexed {stats['total_indexed']} vector embeddings in ChromaDB",
        "details": stats
    }


@router.post("/search/people", response_model=PeopleSearchFilterResponse, status_code=status.HTTP_200_OK)
def search_people_endpoint(
    filters: PeopleSearchFilterRequest,
    db: Session = Depends(get_db)
):
    """
    🔍 Structured Multi-Attribute People & Designation Search:
    
    Filter by:
      - `person_name`: First/last name (e.g. 'Robin Vince', 'Emily')
      - `organization`: Company name or ticker (e.g. 'BNY', 'BK')
      - `designation`: Title keyword (e.g. 'CEO', 'Head of Asset Servicing', 'CTPO')
      - `role`: Seniority tier (e.g. 'CXO', 'VP', 'Managing Director')
      - `department_or_lob`: Division (e.g. 'Asset Servicing', 'Pershing')
      - `min_lead_score`: Minimum score (e.g. 80)
      - `is_decision_maker`: Boolean flag for confirmed buyers
    """
    return search_people_structured(db, filters)


@router.get("/search/organizations", response_model=List[ChatbotOrganizationResult])
def search_organizations_endpoint(
    q: Optional[str] = Query(None, description="Search term for company name, ticker, or industry"),
    db: Session = Depends(get_db)
):
    """
    🏢 Search Organizations & Accounts:
    Returns company overview cards with tech stack, pain points, employee count, and division count.
    """
    query = db.query(Account)
    if q:
        pat = f"%{q.strip()}%"
        query = query.filter(
            (Account.name.ilike(pat)) |
            (Account.publicly_traded_symbol.ilike(pat)) |
            (Account.domain.ilike(pat)) |
            (Account.industry.ilike(pat))
        )
    accounts = query.limit(20).all()
    results = []
    for a in accounts:
        exec_count = db.query(Contact).filter(Contact.account_id == a.id).count()
        lob_count = db.query(AccountLob).filter(AccountLob.account_id == a.id).count()
        tech_list = a.tech_stack if isinstance(a.tech_stack, list) else []
        pain_list = a.pain_points if isinstance(a.pain_points, list) else []
        results.append(ChatbotOrganizationResult(
            id=a.id,
            name=a.name,
            domain=a.domain or "bny.com",
            ticker=a.publicly_traded_symbol,
            exchange=a.publicly_traded_exchange,
            industry=a.industry,
            employee_count=a.employee_count,
            annual_revenue=a.annual_revenue_printed or "$20.0B",
            market_cap=a.market_cap or "$92.7B",
            headquarters=a.headquarters,
            tech_stack=tech_list,
            pain_points=pain_list,
            total_executives=exec_count,
            total_lobs=lob_count
        ))
    return results


@router.get("/suggestions", response_model=ChatbotSuggestionsResponse)
def get_suggestions_endpoint():
    """
    💡 Get Quick-Click Starter Prompts for Sales Reps:
    Returns categorized suggestions to help sales reps start conversational discovery.
    """
    return get_chatbot_starter_prompts()
>>>>>>> 7cf6719 (feat(chatbot): safely integrate core ChromaDB vector store and sales AI conversational chatbot router)

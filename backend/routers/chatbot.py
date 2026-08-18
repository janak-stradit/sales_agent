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

# Sales AI Agent: Embeddings, Vector DB, & RAG Architecture

This document outlines the comprehensive strategy for implementing a Retrieval-Augmented Generation (RAG) pipeline for the Anna Sales Agent. It details how we will use embeddings and a vector database to provide the AI with real-time, accurate, and highly contextual sales intelligence.

---

## 1. The Use Case: Why RAG for Sales AI?

Standard Large Language Models (LLMs) are trained on generalized, historical data. They do not know your specific CRM data, live executive dossiers, recent social posts, or proprietary buying signals. 

**The Problem:** If you ask a standard LLM, "What are the latest buying signals for BNY Mellon?", it will hallucinate or provide outdated information.
**The Solution (RAG):** We vectorize all our proprietary sales data (leads, accounts, signals) and store it in a Vector Database. When a user asks a question, we retrieve the most relevant data chunks and feed them to the LLM as context *before* it generates an answer.

### Key Sales Use Cases Enabled by this Pipeline:
- **Instant Dossier Generation:** "Give me a 360 overview of Emily Portney."
- **Signal Matching:** "Find all VPs in Asset Servicing who recently posted about AI."
- **Account Intelligence:** "Summarize the Q3 technology initiatives for BNY."

---

## 2. Embeddings: Translating Text to Data

Embeddings are numerical representations (vectors) of text. Texts with similar meanings will have vectors that are mathematically close to each other in high-dimensional space.

### Suggested Embedding Models
For a premium enterprise agent, accuracy and speed are critical.
1. **OpenAI `text-embedding-3-small` or `large`:** (Recommended) Highly cost-effective, incredibly fast, and natively supports varying dimensions. Excellent for general enterprise text.
2. **Cohere `embed-english-v3.0`:** Excellent for retrieval tasks, heavily optimized for RAG pipelines.
3. **BGE-M3 (Open Source):** If data privacy is a strict requirement and all processing must remain on-premise, BAAI's BGE models are top-tier open-source alternatives.

### What We Will Embed
- Executive Bios & Roles
- Recent LinkedIn/Social Posts
- Company News & Press Releases
- CRM Notes & Call Transcripts
- Buying Signals & Intent Data

---

## 3. The Vector Database

The Vector Database stores our generated embeddings and allows for lightning-fast **semantic search** (finding data based on meaning, not just exact keyword matches).

### Recommended Solution: ChromaDB (or Pinecone/Qdrant)
Given the existing frontend UI text mentioned *ChromaDB*, it is an excellent choice for our stack.
- **ChromaDB:** Open-source, easily runs locally during development (SQLite-based), and scales well for production. Integrates seamlessly with Python/FastAPI.
- **Pinecone:** Fully managed SaaS, zero infrastructure overhead, extremely fast. (Alternative for enterprise scale).

### Database Schema Concept
Each vector entry will contain metadata to allow for hybrid filtering (Semantic Search + Metadata Filtering):
```json
{
  "id": "doc_123",
  "vector": [0.012, -0.045, 0.112, ...], 
  "text": "Robin Vince announced a major push into AI-driven asset servicing...",
  "metadata": {
    "source_type": "press_release",
    "account_id": "bny_001",
    "executive_id": "rvince_01",
    "timestamp": 1700000000,
    "security_level": "internal_only"
  }
}
```

---

## 4. The RAG Pipeline Autoflow

This is the end-to-end automated flow for how data enters the system and how Anna answers a question.

### Phase A: Ingestion Autoflow (Background Process)
1. **Data Ingestion:** Scrapers, CRM Webhooks, or API integrations pull raw data (e.g., a new executive quote).
2. **Chunking:** Large texts are split into smaller, meaningful chunks (e.g., 500 tokens per chunk) with some overlap to preserve context.
3. **Embedding Generation:** The chunks are sent to the Embedding Model to generate vectors.
4. **Vector Storage:** The vectors + original text + metadata are stored in ChromaDB.

### Phase B: Query & Retrieval Autoflow (User Interaction)
1. **User Prompt:** The user types: *"What is Robin Vince focusing on?"*
2. **Prompt Embedding:** Anna converts the user's question into a vector using the *same* Embedding Model.
3. **Semantic Search (Vector DB):** Anna queries ChromaDB to find the top 5 most mathematically similar text chunks to the question's vector.
4. **Metadata Filtering (Optional):** Anna filters the search (e.g., `WHERE account_id = 'bny_001'`).

### Phase C: Generation Autoflow (LLM Response)
1. **Context Assembly:** The top 5 retrieved text chunks are injected into a hidden System Prompt.
    > *System Prompt: You are Anna. Answer the user's question using ONLY the following context. Context: [Chunk 1], [Chunk 2]...*
2. **LLM Execution:** The core LLM (e.g., GPT-4o, Claude 3.5 Sonnet) processes the prompt + context.
3. **Streaming Response:** Anna streams the highly accurate, hallucination-free response back to the frontend UI.

---

## 5. Integration with Our Current FastAPI Model

To implement this into the current `sales_agent` architecture:

1. **New Services:**
   - Create `backend/services/vector_store.py` (Manages ChromaDB connections and queries).
   - Create `backend/services/embedding_service.py` (Handles calling the OpenAI/Cohere API).
2. **Update `chatbot_service.py`:**
   - Modify the `generate_response()` logic. Instead of just sending the query to the LLM, it will first call `vector_store.search(query)` to fetch context, then append that context to the LLM prompt.
3. **Seed Script Upgrade:**
   - Update `run.py --seed` to not only populate Postgres/SQLite but to also generate embeddings for the seed data (BNY, Robin Vince, Emily Portney) and push them into the local ChromaDB instance.

> [!TIP]
> **Next Steps for Development:**
> If you are ready to build this, our first step should be installing the necessary Python packages (`chromadb`, `openai`, `langchain` if desired) and setting up the local ChromaDB instance inside the backend.

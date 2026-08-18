"""
FastAPI application entry point.
Registers all routers for all 7 Discovery Navigation tabs, Engine Controls, and Sales AI Chatbot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import (
    dashboard_router,
    accounts_router,
    leads_router,
    lobs_router,
    hierarchy_router,
    social_router,
    signals_router,
    pipeline_router,
    logs_router,
    tasks_router,
    chatbot_router,
)

settings = get_settings()

# ── Create FastAPI App ─────────────────────────
app = FastAPI(
    title="Data Discovery / Sales Intelligence Platform",
    description="Multi-Organization Sales Lead Intelligence Engine & B2B Automation Backend with AI Chatbot",
    version="2.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Discovery Navigation & Engine Control Routers ──

# Tab 1: Executive Dashboard
app.include_router(dashboard_router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Executive Dashboard"])

# Tab 2: Target Accounts
app.include_router(accounts_router, prefix=f"{settings.API_V1_PREFIX}/accounts", tags=["Target Accounts"])

# Tab 3: Executive Lead Scoring & Profiles (Matching Screenshot 1)
app.include_router(leads_router, prefix=f"{settings.API_V1_PREFIX}/leads", tags=["Executive Lead Scoring"])

# Supporting: Lines of Business
app.include_router(lobs_router, prefix=f"{settings.API_V1_PREFIX}/lobs", tags=["Lines of Business"])

# Tab 4: Organizational Hierarchy
app.include_router(hierarchy_router, prefix=f"{settings.API_V1_PREFIX}/hierarchy", tags=["Organizational Hierarchy"])

# Tab 5: Social Intelligence
app.include_router(social_router, prefix=f"{settings.API_V1_PREFIX}/social", tags=["Social Intelligence"])

# Tab 6: Sales Trigger Signals
app.include_router(signals_router, prefix=f"{settings.API_V1_PREFIX}/signals", tags=["Sales Trigger Signals"])

# Tab 7: Engine Controls — Pipeline (8 Collection Modes, Matching Screenshot 2)
app.include_router(pipeline_router, prefix=f"{settings.API_V1_PREFIX}/pipeline", tags=["Pipeline & Engine Controls"])

# Tab 7: Engine Controls — Tool Execution Logs & Telemetry
app.include_router(logs_router, prefix=f"{settings.API_V1_PREFIX}/logs", tags=["Telemetry & Audit Logs"])

# Sales AI Conversational Chatbot & People/Designation Search
app.include_router(chatbot_router, prefix=f"{settings.API_V1_PREFIX}/chatbot", tags=["Sales AI Chatbot"])

# Async Tasks
app.include_router(tasks_router, prefix=f"{settings.API_V1_PREFIX}/tasks", tags=["Background Tasks"])


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# ── Health Check & UI Routes ───────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public")

if os.path.exists(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

@app.get("/")
def read_root():
    """Serves the Sales Intelligence Frontend UI."""
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "app_name": "Data Discovery / Sales Intelligence Platform",
        "version": "v2.6.0",
        "environment": settings.ENVIRONMENT,
        "engine": "Multi-Organization Sales Lead Intelligence Engine"
    }

@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "online",
        "app_name": "Data Discovery / Sales Intelligence Platform",
        "version": "v2.6.0",
        "environment": settings.ENVIRONMENT,
    }

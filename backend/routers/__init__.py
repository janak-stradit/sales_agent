"""API Routers registry for Multi-Organization Sales AI Intelligence Platform."""

from .dashboard import router as dashboard_router
from .accounts import router as accounts_router
from .leads import router as leads_router
from .lobs import router as lobs_router
from .hierarchy import router as hierarchy_router
from .social import router as social_router
from .signals import router as signals_router
from .pipeline import router as pipeline_router
from .logs import router as logs_router
from .tasks import router as tasks_router
from .chatbot import router as chatbot_router

__all__ = [
    "dashboard_router",
    "accounts_router",
    "leads_router",
    "lobs_router",
    "hierarchy_router",
    "social_router",
    "signals_router",
    "pipeline_router",
    "logs_router",
    "tasks_router",
    "chatbot_router",
]

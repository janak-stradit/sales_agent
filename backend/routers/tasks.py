"""API endpoint for checking Celery task status."""

from fastapi import APIRouter
from celery.result import AsyncResult
from backend.tasks.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}")
def get_task_status(task_id: str):
    """Check the status of a background Celery task."""
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return response

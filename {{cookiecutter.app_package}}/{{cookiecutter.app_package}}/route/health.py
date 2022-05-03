import celery.exceptions
from fastapi import APIRouter, HTTPException
from structlog import get_logger

from {{ cookiecutter.app_package}}.lib.db import check_db
from {{ cookiecutter.app_package}}.task import health as tasks

TASK_TIMEOUT = 4  # secs

router = APIRouter()
logger = get_logger()


@router.get("/health")
async def get_health() -> dict[str, str]:
    """Verify server health."""
    return {"message": "ok"}


@router.get("/health/log")
async def get_health_log() -> dict[str, str]:
    """Verify server logging health."""
    logger.info("test logging", value=1)
    return {"message": "ok"}


@router.get("/health/task")
async def get_health_task() -> dict[str, str]:
    """Verify async task health."""
    try:
        task = tasks.health.delay(arg="foo")
        result = task.get(timeout=TASK_TIMEOUT)
    except celery.exceptions.TimeoutError:
        raise HTTPException(status_code=500, detail="task timeout")

    return {"message": result}


@router.get("/health/task/db")
async def get_health_task_db() -> dict[str, str]:
    """Verify db in async task health."""
    try:
        task = tasks.health_db.delay()
        result = task.get(timeout=TASK_TIMEOUT)
    except celery.exceptions.TimeoutError:
        raise HTTPException(status_code=500, detail="task timeout")
    return {"message": result}


@router.get("/health/db")
async def get_health_db() -> dict[str, str]:
    """Verify db health."""
    check_db()
    return {"message": "ok"}

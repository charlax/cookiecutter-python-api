from typing import Set

import celery.exceptions
from fastapi import APIRouter, HTTPException, JSONResponse
from structlog import get_logger

from {{ cookiecutter.app_package}}.lib.db import check_db
from {{ cookiecutter.app_package}}.task import health as tasks

TASK_TIMEOUT = 4  # secs

router = APIRouter()
logger = get_logger(__name__)

HEADERS = {"version": config.VERSION_FULL}
RETURNED_CONFIG: Set[str] = {"GIT_SHA", "GIT_REF", "VERSION_FULL", "ENV_NAME"}


@router.get("/health")
async def get_health() -> JSONResponse:
    """Verify server health."""
    return JSONReponse({"message": "ok"}, headers=HEADERS)


@router.get("/health/config")
async def get_health_config() -> dict[str, str]:
    """Verify server config."""
    return {k: getattr(config, k) for k in RETURNED_CONFIG}


@router.get("/health/log")
async def get_health_log() -> dict[str, str]:
    """Verify server logging health."""
    logger.info("test logging", value=1)
    return {"message": "ok"}


@router.get("/health/exception")
async def get_health_exception() -> dict[str, str]:
    """Verify exception handling."""

    class TestingExceptionHandlingException(Exception):
        pass

    raise TestingExceptionHandlingException()


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


@router.get("/health/task/exception")
async def get_health_task_exception() -> dict[str, str]:
    """Call task to test exception handling."""
    tasks.raise_test_exception.delay()
    return {"message": "ok"}


@router.get("/health/db")
async def get_health_db() -> dict[str, str]:
    """Verify db health."""
    check_db()
    return {"message": "ok"}

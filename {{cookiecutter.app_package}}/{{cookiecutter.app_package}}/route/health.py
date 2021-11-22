from fastapi import APIRouter

from {{ cookiecutter.app_package}}.lib.db import check_db

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, str]:
    return {"message": "ok"}


@router.get("/health/db")
async def get_health_db() -> dict[str, str]:
    check_db()
    return {"msg": "ok"}

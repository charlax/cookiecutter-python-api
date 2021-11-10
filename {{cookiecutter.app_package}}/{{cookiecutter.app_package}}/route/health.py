from fastapi import APIRouter

from {{ cookiecutter.app_package}}.lib.db import check_db, engine_url
from {{ cookiecutter.app_package}}.config import MisconfiguredException

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, str]:
    return {"message": "ok"}


@router.get("/health/db")
async def get_health_db() -> dict[str, str]:
    if engine_url.password == "unconfigured":
        raise MisconfiguredException("db password is not configured")
    check_db()
    return {"msg": "ok"}

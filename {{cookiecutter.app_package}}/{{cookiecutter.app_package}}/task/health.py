import structlog

from {{cookiecutter.app_package}}.lib.db import check_db
from {{cookiecutter.app_package}}.lib.task import app

logger = structlog.get_logger(__name__)


@app.task
def health(arg: str = "") -> str:
    logger.info("logging in health task", arg=arg)
    return f"ok, got arg: {arg!r}"


@app.task
def health_db() -> str:
    check_db()
    return "ok"

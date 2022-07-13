import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from structlog import get_logger

from {{cookiecutter.app_package}}.config import config

logger = get_logger(__name__)


def setup_sentry() -> None:  # nocov
    logger.debug("setting up Sentry")
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        release=f"{{cookiecutter.app_package}}@{config.VERSION}+{config.GIT_SHA}",
        environment=config.ENV_NAME,
        traces_sample_rate=0,
        with_locals=False,
        max_breadcrumbs=0,
        request_bodies="never",
        integrations=[
            CeleryIntegration(),
        ],
    )

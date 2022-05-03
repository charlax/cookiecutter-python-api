import logging
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from asgi_correlation_id.context import correlation_id
from asgi_correlation_id.extensions.celery import load_correlation_ids

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.json_encoder import forgiving_dumps

# Transfer the request id to the task
load_correlation_ids()


def add_version(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> dict[str, Any]:
    """Add version to log message."""
    # app version is set in main.py
    if config.GIT_SHA:
        event_dict["git_sha"] = config.GIT_SHA
    return event_dict


def add_correlation(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> dict[str, Any]:
    """Add request id to log message."""
    if request_id := correlation_id.get():
        event_dict["request_id"] = request_id
    return event_dict


class ConsoleRenderer(structlog.dev.ConsoleRenderer):
    def _repr(self, val: Any) -> str:
        # Display shorter uuid
        # https://www.structlog.org/en/stable/_modules/structlog/dev.html#ConsoleRenderer
        if isinstance(val, UUID):
            return str(val)
        if isinstance(val, Path):
            return str(val)
        return super()._repr(val)


def setup_logging(
    level: str = "INFO",
    *,
    is_console: Optional[bool] = None,
    bind: Optional[Dict[str, Any]] = None,
) -> None:
    """Configure logging.

    :param is_console: should be True for console (dev) environment.
    :param bind: extra key-values to log with all messages

    """
    is_console = is_console if is_console is not None else config.USE_CONSOLE_LOGGING
    # see https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format="%(message)s", level=level)

    if not is_console:
        processors = [
            # Must be first
            structlog.contextvars.merge_contextvars,
            add_correlation,
            add_version,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(serializer=forgiving_dumps),
        ]
    else:  # nocov
        processors = [
            # Must be first
            structlog.contextvars.merge_contextvars,
            add_correlation,
            add_version,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,  # type: ignore
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

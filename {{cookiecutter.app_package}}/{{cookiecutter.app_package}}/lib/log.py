import logging
from typing import Any
from uuid import UUID

import structlog

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.json_encoder import dumps


def add_version(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add version to log message."""
    event_dict["version"] = config.git_commit_short
    return event_dict


class ConsoleRenderer(structlog.dev.ConsoleRenderer):
    def _repr(self, val: Any) -> str:
        # Display shorter uuid
        # https://www.structlog.org/en/stable/_modules/structlog/dev.html#ConsoleRenderer
        if isinstance(val, UUID):
            return str(val)
        return super()._repr(val)


def setup_logging(level: str = "INFO", *, is_console: bool = False) -> None:
    """Configure logging.

    console should be True for console (dev) environment.
    """
    # see https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format="%(message)s", level=level)

    if not is_console:
        processors = [
            add_version,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(serializer=dumps),
        ]
    else:  # nocov
        processors = [
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

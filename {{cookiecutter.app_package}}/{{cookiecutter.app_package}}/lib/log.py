import logging
from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional, cast
from uuid import UUID

import structlog
from asgi_correlation_id.context import (
    celery_current_id,
    celery_parent_id,
    correlation_id,
)
from asgi_correlation_id.extensions.celery import (
    load_celery_current_and_parent_ids,
    load_correlation_ids,
)

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.json_encoder import forgiving_dumps

# Transfer the request id to the task
# https://github.com/snok/asgi-correlation-id
load_correlation_ids()
load_celery_current_and_parent_ids()

_LOGGING_CONFIGURED = False

CELERY_LOGGER_NAMES: List[str] = ["celery.app.trace", "celery.worker.strategy"]
CELERY_TRACE_DATA: Dict[str, str] = {
    # See celery.app.trace source for details
    # old_key: new_key
    "name": "_task_name",
    "id": "_task_id",
    "return_value": "return_value",
    "runtime": "runtime",
}


def add_variables(bind: Dict[str, Any]) -> structlog.types.Processor:
    def add_variables_inner(
        logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """Add other variables to log message."""
        event_dict.update(bind)
        return event_dict

    return add_variables_inner


def add_correlation(
    logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Add request id to log message."""
    if request_id := correlation_id.get():
        event_dict["_request_id"] = encode_uuid(request_id)
    if _celery_parent_id := celery_parent_id.get():
        event_dict["_celery_parent_id"] = encode_uuid(_celery_parent_id)
    if _celery_current_id := celery_current_id.get():
        event_dict["_celery_id"] = encode_uuid(_celery_current_id)
    return event_dict


def handle_celery_app_trace(
    logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Explode extra's data attribute on celery.app.trace log records."""
    log_record = event_dict.get("_record")
    if not log_record or log_record.name not in CELERY_LOGGER_NAMES:
        return event_dict

    # The ExtraAdder adds the "extra" inside the records and has been
    # applied before.
    data = event_dict.get("data", {})
    for key, new_key in CELERY_TRACE_DATA.items():
        value = data.pop(key, "")
        if value:
            # Do not override existing values
            event_dict.setdefault(new_key, value)

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
    # If you need to modify this, make sure you read structlog's doc first:
    # https://www.structlog.org/en/stable/standard-library.html
    # See "Rendering Using structlog-based Formatters Within logging"
    global _LOGGING_CONFIGURED

    is_console = is_console if is_console is not None else config.USE_CONSOLE_LOGGING

    # Avoid configuring logging twice
    if _LOGGING_CONFIGURED:
        return
    _LOGGING_CONFIGURED = True

    # see https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    extra = {"_version": config.VERSION}
    if config.GIT_SHA:
        extra["_sha"] = config.GIT_SHA

    processors: List[structlog.types.Processor] = [
        # Must be first
        structlog.contextvars.merge_contextvars,
        add_correlation,
        add_variables(extra),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=cast(
            List[structlog.types.Processor],
            [
                # Should be the first to stop all potentially expensive processing
                # if we know that this level is filtered out.
                structlog.stdlib.filter_by_level,
            ],
        )
        + processors
        + [
            # convert the event dict into something ProcessorFormatter understands
            # (see structlog docs)
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        context_class=dict,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=processors
        + [
            structlog.stdlib.ExtraAdder(),
            handle_celery_app_trace,
        ],
        # These run on ALL entries after the pre_chain is done.
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Send everything to stdout
    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setFormatter(formatter)

    root_logger = logging.getLogger("{{ cookiecutter.app_package }}")
    root_logger.addHandler(handler_stream)
    root_logger.setLevel(logging.INFO)

    for name in CELERY_LOGGER_NAMES:
        logger = logging.getLogger(name)
        logger.addHandler(handler_stream)
        logger.setLevel(logging.INFO)

    # Prevent double logging to Sentry
    # https://stackoverflow.com/questions/68733567/uvicorn-fastapi-duplicate-logging
    uvicorn = logging.getLogger("uvicorn.error")
    uvicorn.propagate = False
    uvicorn.handlers = []

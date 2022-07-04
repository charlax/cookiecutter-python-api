from datetime import timedelta
from typing import Any

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_init

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.log import setup_logging

beat_schedule = {
    "recurring_task_name": {
        "task": "{{cookiecutter.app_package}}.service.foo.do_stuff",
        # Every 30 minutes
        "schedule": crontab(minute="*/30"),
    },
}

app = Celery(
    "{{cookiecutter.app_package}}_worker",
    backend=config.CELERY_RESULT_BACKEND,
    broker=config.CELERY_BROKER_URL,
    result_backend_transport_options={"retry_policy": {"timeout": 5.0}},
    result_extended=True,
    result_expires=timedelta(hours=24),
    beat_schedule=beat_schedule,
    task_time_limit=3600,  # hard limit
    task_soft_time_limit=3600,  # soft limit
    task_track_started=True,
)

@worker_init.connect  # type: ignore
def at_worker_init(*args: Any, **kwargs: Any) -> None:
    setup_logging()
    setup_sentry()

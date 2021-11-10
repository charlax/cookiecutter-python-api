from fastapi import FastAPI

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.log import setup_logging
from {{cookiecutter.app_package}}.route import health


setup_logging(is_console=config.use_console_logging)

ROUTERS = [health]

app = FastAPI()

for module in ROUTERS:
    app.include_router(module.router)  # type: ignore

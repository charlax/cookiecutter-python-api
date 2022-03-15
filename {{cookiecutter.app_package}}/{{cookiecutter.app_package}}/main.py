from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.log import setup_logging
from {{cookiecutter.app_package}}.route import health


setup_logging(is_console=config.USE_CONSOLE_LOGGING)

ROUTERS = [health]

app = FastAPI(version="0.1.1")
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"]
)


for module in ROUTERS:
    app.include_router(module.router)  # type: ignore

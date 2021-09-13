from fastapi import FastAPI

from {{cookiecutter.app_package}}.route import health

ROUTERS = [health]

app = FastAPI()

for module in ROUTERS:
    app.include_router(module.router)  # type: ignore

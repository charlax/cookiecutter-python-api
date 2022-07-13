import time
from typing import Awaitable, Callable

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from {{cookiecutter.app_package}}.config import config
from {{cookiecutter.app_package}}.lib.log import setup_logging
from {{cookiecutter.app_package}}.lib.sentry import setup_sentry
from {{cookiecutter.app_package}}.route import health


ROUTERS = [health]

app = FastAPI(
    version=config.VERSION,
    description="API description",
    contact={"name": "YOUR_NAME"},
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=[config.BASE_API_URL.host, "127.0.0.1", "localhost"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods="*",
    allow_headers=["Authorization"],
)

setup_logging(bind={"app_version": app.version})

logger = structlog.get_logger(__name__)

if config.IS_SENTRY_ENABLED:
    setup_sentry()
    app.add_middleware(SentryAsgiMiddleware)

Middleware = Callable[[Request], Awaitable[Response]]


@app.middleware("http")
async def request_middleware(request: Request, call_next: Middleware) -> Response:
    structlog.contextvars.clear_contextvars()

    # Requests: https://github.com/encode/starlette/blob/master/starlette/requests.py
    logger.info(
        "request started",
        method=request.method,
        path=request.url.path,
        client=request.client and request.client.host,
        ua=request.headers.get("User-Agent"),
    )

    start = time.perf_counter()
    response = await call_next(request)
    end = time.perf_counter()

    logger.info(
        "request ended",
        method=request.method,
        path=request.url.path,
        client=request.client and request.client.host,
        ua=request.headers.get("User-Agent"),
        status_code=response.status_code,
        elapsed_ms=int((end - start) * 1000),
    )

    # Security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# Order matters: this middleware needs to be installed last
app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Example taken from https://github.com/snok/asgi-correlation-id
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            "Internal server error",
            headers={
                "X-Correlation-ID": correlation_id.get() or "",
                "Access-Control-Expose-Headers": "X-Correlation-ID",
            },
        ),
    )


for module in ROUTERS:
    app.include_router(module.router)  # type: ignore

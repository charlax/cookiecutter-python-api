import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings
from structlog import get_logger

BASE_ENV_FILENAME = ".env"
ENV_FILENAME = os.environ.get("DOTENV", BASE_ENV_FILENAME)
UNCONFIGURED = "unconfigured"

logger = get_logger(__name__)


class MisconfiguredException(Exception):
    pass


class Config(BaseSettings):
    class Config:
        # https://pydantic-docs.helpmanual.io/usage/settings/#use-case-docker-secrets
        secrets_dir = "/run/secrets"

    # Please use env_name ONLY for informational purpose
    ENV_NAME: str

    GIT_SHA: str = ""

    DB_USER: str = UNCONFIGURED
    DB_PASSWORD: str = UNCONFIGURED
    DB_NAME: str = UNCONFIGURED
    DB_PORT: str = "5432"
    DB_HOST: str = "localhost"

    BASE_API_URL: AnyHttpUrl

    # Set to true for local dev
    USE_CONSOLE_LOGGING: bool = False


def get_config() -> Config:
    """Get the config."""
    # We follow serverless's dotenv behavior here:
    # https://www.npmjs.com/package/serverless-dotenv-plugin
    # .env -> .env.{env} -> .env.{env}.local

    def try_load(filename: str) -> None:
        if not filename or not Path(filename).exists():
            return
        load_dotenv(dotenv_path=filename)
        logger.debug("config loaded", filename=filename)

    # To allow overriding with env var, we load by order of decreasing
    # specificity

    if ENV_FILENAME and ENV_FILENAME.endswith(".local"):
        raise ValueError(
            "Expected env filename like '.env.dev', "
            f"got override ending with .local instead: {ENV_FILENAME!r}. "
            f" Try with {ENV_FILENAME.replace('.local', '')!r}"
        )

    # Load .env.{env}.local if it exists
    try_load(ENV_FILENAME + ".local")
    try_load(ENV_FILENAME)
    try_load(BASE_ENV_FILENAME)

    return Config()


config = get_config()

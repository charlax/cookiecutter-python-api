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

    # First load .env
    load_dotenv(dotenv_path=BASE_ENV_FILENAME, override=True)
    logger.debug("config loaded", filename=BASE_ENV_FILENAME)

    if not Path(ENV_FILENAME).exists():
        raise ValueError(f"Config file {ENV_FILENAME} does not exist.")

    if ENV_FILENAME.endswith(".local"):
        raise ValueError(
            "Expected env filename like '.env.dev', "
            f"got override ending with .local instead: {ENV_FILENAME!r}. "
            f" Try with {ENV_FILENAME.replace('.local', '')!r}"
        )

    # Then load .env.{env}
    if ENV_FILENAME != BASE_ENV_FILENAME:
        load_dotenv(dotenv_path=ENV_FILENAME, override=True)
        logger.debug("config loaded", filename=ENV_FILENAME)

    # Then load .env.{env}.local if it exists
    override = ENV_FILENAME + ".local"
    if Path(override).exists():
        load_dotenv(dotenv_path=override, override=True)
        logger.debug("config loaded", filename=override)

    return Config()


config = get_config()

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings

ENV_FILENAME = os.environ.get("DOTENV", ".env")


class MisconfiguredException(Exception):
    pass


class Config(BaseSettings):
    # Please use env_name ONLY for informational purpose
    env_name: str
    git_commit_short: str = "unknown"

    db_user: str = "unconfigured"
    db_password: str = "unconfigured"
    db_name: str = "unconfigured"
    db_port: str = "5432"
    db_host: str = "localhost"


def get_config() -> Config:
    """Get the config."""
    # We follow serverless's dotenv behavior here:
    # https://www.npmjs.com/package/serverless-dotenv-plugin

    # First load .env
    load_dotenv(dotenv_path=".env")

    if not Path(ENV_FILENAME).exists():
        raise ValueError(f"Config file {ENV_FILENAME} does not exist.")

    if ENV_FILENAME.endswith(".local"):
        raise ValueError(
            "Expected env filename like '.env.dev', "
            f"got override ending with .local instead: {ENV_FILENAME!r}. "
            f" Try with {ENV_FILENAME.replace('.local', '')!r}"
        )

    # Then load .env.{env}
    load_dotenv(dotenv_path=ENV_FILENAME)

    # Then load .env.{env}.local if it exists
    override = ENV_FILENAME + ".local"
    if Path(override).exists():
        load_dotenv(dotenv_path=override)

    return Config()


config = get_config()

import importlib
import pkgutil

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from {{ cookiecutter.app_package}}.config import config

engine_url = URL.create(
    drivername="postgresql+psycopg2",
    username=config.db_user,
    password=config.db_password,
    host=config.db_host,
    port=config.db_port,
    database=config.db_name,
)
engine = create_engine("TODO", future=True)
session = Session(engine)
Base = declarative_base()


def import_all_repos() -> None:
    """Import all repos to make sure the mapper is fully initialized."""
    from {{ cookiecutter.app_package}} import repo

    def not_test(p):  # type: ignore
        return "test" not in p.name

    packages = pkgutil.walk_packages(repo.__path__, prefix=repo.__name__ + ".")  # type: ignore
    for p in filter(not_test, packages):
        importlib.import_module(p.name)


def check_db() -> None:  # nocov
    """Ensure the connection with the DB works."""
    with engine.connect() as conn:
        result = conn.execute(text("select 1"))
        value = result.fetchone()[0]
        assert value == 1

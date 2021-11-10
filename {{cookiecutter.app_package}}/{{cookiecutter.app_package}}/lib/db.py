import importlib
import pkgutil
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

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
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
        if value != 1:
            raise ValueError(f"Expected 1, got {value}")

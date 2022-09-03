import importlib
import pkgutil
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Type

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from {{ cookiecutter.app_package}}.config import config

engine_url = URL.create(
    drivername="postgresql+psycopg2",
    username=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    database=config.DB_NAME,
)
engine = create_engine("TODO", future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db(session_cls: Optional[Type[Session]] = None) -> Iterator[Session]:
    # We catch the reference to SessionLocal at runtime to allow mocking
    db = (session_cls or SessionLocal)()
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
    if engine_url.password == "unconfigured":
        raise MisconfiguredException("db password is empty, check env and config")

    with engine.connect() as conn:
        result = conn.execute(text("select 1"))
        value = result.fetchone()[0]
        if value != 1:
            raise ValueError(f"Expected 1, got {value}")


def update_record(record: Base, update_request: Any) -> None:
    """Update a record based on an update request.

    The current implementation only allows None as 'not provided' value.
    """
    for key, value in update_request:
        if not value:
            continue
        setattr(record, key, value)

import importlib
import pkgutil

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine = create_engine("TODO", future=True)
session = Session(engine)
Base = declarative_base()


def import_all_repos():
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
        result = conn.execute("select 1")
        value = result.fetchone()[0]
        assert value == 1

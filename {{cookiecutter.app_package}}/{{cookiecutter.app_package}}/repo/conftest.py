import pytest
from sqlalchemy.orm import sessionmaker

from {{cookiecutter.app_package}}.lib.db import engine

Session = sessionmaker()


@pytest.fixture(autouse=True)
def db(mocker):  # type: ignore
    # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html
    conn = engine.connect()
    trans = conn.begin()

    session = Session(bind=conn)

    mocker.patch("{{cookiecutter.app_package}}.lib.db.Session", lambda: session)

    yield session

    session.close()
    trans.rollback()
    conn.close()

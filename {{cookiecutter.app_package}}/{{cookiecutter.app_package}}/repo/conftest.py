import pytest
from sqlalchemy import SessionLocal

from {{cookiecutter.app_package}}.lib.db import engine


@pytest.fixture(autouse=True)
def db(mocker):  # type: ignore
    # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html
    conn = engine.connect()
    trans = conn.begin()

    session = SessionLocal(bind=conn)

    mocker.patch("app.lib.db.SessionLocal", lambda: session)

    yield session

    session.close()
    trans.rollback()
    conn.close()

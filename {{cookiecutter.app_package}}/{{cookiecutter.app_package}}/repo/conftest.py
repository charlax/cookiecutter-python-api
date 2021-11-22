import pytest

from {{cookiecutter.app_package}}.lib.db import engine, SessionLocal

Session = sessionmaker()


@pytest.fixture(autouse=True)
def db(mocker):  # type: ignore
    # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html
    conn = engine.connect()
    trans = conn.begin()

    session = SessionLocal(bind=conn)

    mocker.patch("{{cookiecutter.app_package}}.lib.db.SessionLocal", lambda: session)

    yield session

    session.close()
    trans.rollback()
    conn.close()

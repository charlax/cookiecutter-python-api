from typing import Any, Optional
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, String, create_engine, types
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import declarative_base, sessionmaker

from {{cookiecutter.app_package}}.repo.base import Repository

Base = declarative_base()
engine = create_engine("sqlite:///:memory:", future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UUIDC(types.TypeDecorator[UUID]):
    # See:
    # https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    impl = types.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        return dialect.type_descriptor(types.CHAR(32))  # type: ignore

    def process_bind_param(self, value: Any, dialect: Dialect) -> Optional[str]:
        if not value:
            return None

        parsed: UUID = UUID(value) if not isinstance(value, UUID) else value
        return parsed.hex

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[UUID]:
        if not value:
            return None

        parsed: UUID = UUID(value) if not isinstance(value, UUID) else value
        return parsed


class Fake(BaseModel):
    class Config:
        orm_mode = True

    id: UUID
    name: str


class TFake(Base):
    __tablename__ = "fakes"

    id: UUID = Column(UUIDC(), default=lambda: str(uuid4()), primary_key=True)
    name = Column(String, nullable=False)


repo = Repository(  # type: ignore[type-var]
    record_cls=TFake,
    domain_cls=Fake,
    session_cls=SessionLocal,
)


@pytest.fixture(autouse=True, scope="module")
def setup_db() -> None:
    Base.metadata.create_all(engine)


@pytest.fixture
def saved() -> Fake:
    return repo.create(Fake(id=uuid4(), name="toaster"))


def test_get(saved: Fake) -> None:
    fake = repo.get(saved.id)
    assert fake is not None
    assert fake.id == saved.id


def test_get_nonexisting() -> None:
    fake = repo.get(uuid4())
    assert fake is None

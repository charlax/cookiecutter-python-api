import uuid

from sqlalchemy import Column, String, select
from sqlalchemy_utils import UUIDType

from {{cookiecutter.app_package}}.domain.foo import Foo
from {{cookiecutter.app_package}}.lib.db import Base, session


class TFoo(Base):
    __tablename__ = "foos"
    id = Column(UUIDType, default=uuid.uuid4, primary_key=True)
    name = Column(String())


def get(job_id: uuid.UUID) -> Foo:
    stmt = select(TFoo).where(TFoo.id == job_id)
    record = session.execute(stmt)
    return Foo.from_orm(record)


def create(name: str) -> Foo:
    record = TFoo(name=name)
    session.add(record)
    session.commit()

    return Foo.from_orm(record)

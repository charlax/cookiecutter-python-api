import uuid

from sqlalchemy import Column, String, select
from sqlalchemy_utils import UUIDType

from {{cookiecutter.app_package}}.domain.foo import Foo
from {{cookiecutter.app_package}}.lib.db import Base, session


class TFoo(Base):
    __tablename__ = "foos"
    id = Column(UUIDType, default=uuid.uuid4, primary_key=True)
    name = Column(String())


def get(job_id: uuid.UUID) -> Job:
    stmt = select(TFoo).where(TFoo.id == job_id)
    record = session.execute(stmt)
    return Job.from_orm(record)


def create(name: str) -> Job:
    record = TFoo(name=name)
    session.add(record)
    session.commit()

    return Foo.from_orm(record)

from uuid import UUID, uuid4

from sqlalchemy import DateTime, Column, func, String, select
from sqlalchemy.dialects.postgresql import UUID as UUIDC

from {{cookiecutter.app_package}}.domain.foo import Foo, FooUpdate
from {{cookiecutter.app_package}}.lib.db import Base, get_db, update_record


class TFoo(Base):
    __tablename__ = "foos"
    id: UUID = Column(UUIDC(as_uuid=True), default=uuid4, primary_key=True)
    name = Column(String())

    created_at = Column(DateTime(timezone=True), server_default=func.now())


def get(job_id: UUID) -> Foo:
    with get_db() as session:
        stmt = select(TFoo).where(TFoo.id == job_id)
        record = session.execute(stmt).scalar_one_or_none()
        return Foo.from_orm(record)


def create(name: str) -> Foo:
    with get_db() as session:
        record = TFoo(name=name)
        session.add(record)
        session.commit()

        return Foo.from_orm(record)


def update(id: UUID, update_request: FooUpdate) -> Foo:
    """Update a foo."""
    stmt = select(TFoo).where(TFoo.id == id)
    with get_db() as session:
        record = session.execute(stmt).scalar_one_or_none()
        if not record:
            raise NotFoundException(f"Foo {id} not found")

        update_record(record, update)
        session.commit()

    return get(id)

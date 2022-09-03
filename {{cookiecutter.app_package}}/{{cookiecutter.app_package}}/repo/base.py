from contextlib import contextmanager
from typing import Any, Generic, Iterator, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from {{cookiecutter.app_package}}.lib.db import Base, get_db

R = TypeVar("R", bound=Base)
D = TypeVar("D", bound=BaseModel)

# Typical features to add here:
# - Handle updates
# - Handle which attr can be updated
# - Handle soft and hard deletes


class Repository(Generic[R, D]):
    """
    Simplify handling simple repository operations.
    This class assumes that the record object has an `id` UUID column.
    """

    def __init__(
        self,
        record_cls: Type[R],
        domain_cls: Type[D],
        session_cls: Optional[Any] = None,
    ) -> None:
        self.record_cls = record_cls
        self.domain_cls = domain_cls

        self.session_cls = session_cls

    @contextmanager
    def get_db(self) -> Iterator[Session]:
        """Get db connection."""
        with get_db(self.session_cls) as db:
            yield db

    def get_record_from_domain(self, domain: D) -> R:
        """Create record from domain object."""
        return self.record_cls(**(domain.dict()))

    def get(self, id: UUID) -> Optional[D]:
        """Get a record and return it as a domain object."""
        stmt = select(self.record_cls).where(self.record_cls.id == id)  # type: ignore
        with self.get_db() as session:
            record = session.execute(stmt).scalar_one_or_none()
            if not record:
                return None

            return self.domain_cls.from_orm(record)

    def create(self, request: Any) -> D:
        """Create a record from a domain object."""
        with self.get_db() as session:
            record = self.get_record_from_domain(request)
            session.add(record)
            session.commit()
            returned = self.get(record.id)  # type: ignore[attr-defined]
            assert returned is not None  # nosec
            return returned

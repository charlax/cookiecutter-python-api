from uuid import UUID

from pydantic import BaseModel


class Foo(BaseModel):
    id: UUID

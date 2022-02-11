from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class Foo(BaseModel):
    class Config:
        orm_mode = True

    id: UUID
    name: str


class FooUpdate(BaseModel):
    name: Optional[str] = None

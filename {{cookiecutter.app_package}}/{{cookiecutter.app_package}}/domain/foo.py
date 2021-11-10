from uuid import UUID

from pydantic import BaseModel


class Foo(BaseModel):
    class Config:
        orm_mode = True

    id: UUID

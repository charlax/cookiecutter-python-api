import json
from enum import Enum
from typing import Any
from uuid import UUID


def default(obj: Any, *, is_forgiving: bool = False) -> Any:
    if isinstance(obj, UUID):
        return str(obj)

    if issubclass(obj.__class__, Enum):
        return obj.value

    if not is_forgiving:
        raise TypeError(f"Can't serialize {type(obj)}")

    return str(obj)


def dumps(*args: Any, **kwargs: Any) -> str:
    """Dump as json, supporting UUID and Enum."""
    kwargs.pop("default", None)
    return json.dumps(*args, **kwargs, default=default)


def forgiving_dumps(*args: Any, **kwargs: Any) -> str:
    """Dump as json, supporting UUID and Enum."""
    kwargs.pop("default", None)
    return json.dumps(*args, **kwargs, default=lambda v: default(v, is_forgiving=True))

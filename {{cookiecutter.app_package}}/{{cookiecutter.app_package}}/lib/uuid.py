from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Union
from uuid import UUID


def encode_uuid(value: Union[UUID, str]) -> str:
    """Encode a UUID in a shorter representation."""
    value_uuid = value if isinstance(value, UUID) else UUID(value)
    return urlsafe_b64encode(value_uuid.bytes).rstrip(b"=").decode("ascii")


def decode_uuid(encoded: str) -> UUID:
    """Decode a UUID from a shorter representation."""
    return UUID(bytes=urlsafe_b64decode(encoded + "=="))

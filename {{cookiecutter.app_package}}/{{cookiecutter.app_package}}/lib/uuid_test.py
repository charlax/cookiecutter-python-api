from uuid import UUID

from {{cookiecutter.app_package}}.lib.uuid import decode_uuid, encode_uuid

TEST_UUID = UUID("{decade00-0000-4000-a000-000000000000}")
TEST_ENCODED = "3sreAAAAQACgAAAAAAAAAA"


def test_encode_uuid() -> None:
    assert encode_uuid(TEST_UUID) == TEST_ENCODED


def test_decode_uuid() -> None:
    assert decode_uuid(TEST_ENCODED) == TEST_UUID

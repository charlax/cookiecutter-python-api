from typing import Any


def test_health(client: Any) -> None:
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"message": "ok"}

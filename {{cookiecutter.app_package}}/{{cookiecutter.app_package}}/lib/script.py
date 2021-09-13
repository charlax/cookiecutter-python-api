from app.lib.logging import setup_logging


def setup() -> None:
    setup_logging(console=True)

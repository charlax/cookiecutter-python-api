from {{cookiecutter.app_package}}.lib.log import setup_logging


def setup() -> None:
    setup_logging(is_console=True)

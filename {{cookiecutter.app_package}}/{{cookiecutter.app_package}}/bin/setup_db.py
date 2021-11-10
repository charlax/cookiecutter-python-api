#!/usr/bin/env python3
import argparse
import sys

from {{cookiecutter.app_package}}.lib.db import Base, engine, import_all_repos
from {{cookiecutter.app_package}}.lib.script import setup_for_script


def main() -> int:
    import_all_repos()
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)
    return 0


if __name__ == "__main__":
    setup_for_script()

    parser = argparse.ArgumentParser(description="setup the db")
    args = parser.parse_args()

    sys.exit(main())

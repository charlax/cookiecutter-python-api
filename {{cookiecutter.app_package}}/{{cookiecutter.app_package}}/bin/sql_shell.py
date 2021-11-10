#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess

from {{ cookiecutter.app_package}}.lib.db import engine_url as url
from {{ cookiecutter.app_package}}.lib.script import setup_for_script


def main() -> int:
    cmd = list(map(str, ["psql", "-h", url.host, "-p", url.port, "-U", url.username, "-d", url.database]))
    os.environ["PGPASSWORD"] = str(url.password)
    subprocess.run(cmd)
    return 0


if __name__ == "__main__":
    setup_for_script()

    parser = argparse.ArgumentParser(description="start SQL shell")
    args = parser.parse_args()

    sys.exit(main())

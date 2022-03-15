#!/usr/bin/env python3
import argparse
import sys

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from {{ cookiecutter.app_package}}.config import config


def main(db_name: str, db_user: str, db_password: str) -> int:
    conn = psycopg2.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database="template1",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    exists = cur.execute(
        "select exists(SELECT datname FROM pg_catalog.pg_database "
        "WHERE lower(datname) = lower(%s));",
        (db_name,),
    )

    # Disconnect everyone
    if exists:
        cur.execute(f"REVOKE CONNECT ON DATABASE {db_name} FROM PUBLIC;")
        cur.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;")

    print(f"DANGEROUS: this will drop everything on {db_name}")
    cur.execute(sql.SQL("drop database if exists {}").format(sql.Identifier(db_name)))
    cur.execute(sql.SQL("create database {}").format(sql.Identifier(db_name)))
    cur.execute(
        sql.SQL("drop user if exists {}").format(
            sql.Identifier(db_user), sql.Identifier(db_password)
        )
    )
    cur.execute(
        sql.SQL("create user {} with password %s").format(sql.Identifier(db_user)),
        (db_password,),
    )
    cur.execute(
        sql.SQL("grant all privileges on database {} TO {};").format(
            sql.Identifier(db_name), sql.Identifier(db_user)
        )
    )

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    sys.exit(main(db_name=args.name, db_user=args.user, db_password=args.password))

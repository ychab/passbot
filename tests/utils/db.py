from typing import cast

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Connection, Engine, make_url

from psycopg2.errorcodes import INVALID_CATALOG_NAME

from passbot.config import settings
from passbot.db import SessionFactory, SessionScoped, engine

test_engine: Engine


def init_db(test_db_name: str):
    conn = engine.connect()  # Connect to the CURRENT database
    conn.execute(text("commit"))  # Leave the transaction

    # First cleanup by drop (if any) and create test DB.
    try:
        drop_test_database(conn, test_db_name)
        create_test_database(conn, test_db_name)
    finally:
        conn.close()


def drop_test_database(conn: Connection, test_db_name: str):
    try:
        conn.execute(text(f"DROP DATABASE {test_db_name}"))
    except sqlalchemy.exc.ProgrammingError as exc:  # pragma: no cover
        if exc.orig.pgcode != INVALID_CATALOG_NAME:  # type: ignore
            raise exc
    finally:
        conn.execute(text("commit"))


def create_test_database(conn: Connection, test_db_name: str):
    conn.execute(text(f"CREATE DATABASE {test_db_name}"))
    conn.execute(text("commit"))


def configure_sessionmakers(test_db_name: str) -> None:
    global test_engine  # Booooo, shame on you!

    url: URL = make_url(cast(str, settings.SQLALCHEMY_DATABASE_URI))
    url = url.set(database=test_db_name)

    # Create a new engine for the testing DB
    test_engine = create_engine(url=url)

    # Then reconfigure global sessionmakers to use it... Tada!
    SessionFactory.configure(bind=test_engine)
    SessionScoped.configure(bind=test_engine)

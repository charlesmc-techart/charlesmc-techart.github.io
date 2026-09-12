import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import g

type Table = list[sqlite3.Row]


# Custom converters ###########################################################


def format_date(value: bytes) -> str:
    """Format the date bytes retrieved from a SQLite3 database.

    :param value: The date in ISO format
    :return: `Present` or `MMM YYYY` where `MMM` is the 3-letter abbreviation of the month
    """

    decoded_value = value.decode("utf-8")
    if decoded_value == "9999-12-31":
        return "Present"
    return date.fromisoformat(decoded_value).strftime("%b %Y")


sqlite3.register_converter("py_date", format_date)


# Database operations #########################################################


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            f"file:{os.getenv('DATABASE')}?mode=ro",
            uri=True,
            detect_types=sqlite3.PARSE_COLNAMES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)

    if db is not None:
        db.close()


def read_sql_file(filename: str) -> str:
    with Path(__file__).with_name(filename).open() as f:
        return f.read()


def fetch_data(cursor: sqlite3.Cursor, sql: str) -> list[sqlite3.Row]:
    return cursor.execute(sql).fetchall()

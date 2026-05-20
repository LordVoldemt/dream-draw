from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "migrations" / "001_initial.sql"


def normalize_database_url(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite database URLs are supported in the current implementation.")
    relative_path = database_url.replace("sqlite:///", "", 1)
    return Path(relative_path)


class Database:
    def __init__(self, database_url: str) -> None:
        self.path = normalize_database_url(database_url)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self.connection() as connection:
            schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
            connection.executescript(schema_sql)
            connection.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

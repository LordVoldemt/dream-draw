from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "migrations" / "001_initial.sql"

COMPATIBLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "generation_tasks": (
        "reference_mode TEXT",
        "reference_image_count INTEGER NOT NULL DEFAULT 0",
        "provider_id TEXT",
        "finished_at TEXT",
    ),
    "works": (
        "prompt_snapshot TEXT",
        "style_id TEXT",
        "template_id TEXT",
        "ratio_id TEXT",
        "quality_level TEXT",
        "reference_mode TEXT",
        "reference_image_count INTEGER DEFAULT 0",
        "final_points INTEGER DEFAULT 0",
    ),
}


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
            self._apply_compatible_migrations(connection)
            connection.commit()

    def _apply_compatible_migrations(self, connection: sqlite3.Connection) -> None:
        for table_name, column_definitions in COMPATIBLE_COLUMNS.items():
            existing_columns = {
                row["name"]
                for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
            }
            for column_definition in column_definitions:
                column_name = column_definition.split(maxsplit=1)[0]
                if column_name not in existing_columns:
                    connection.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_definition}",
                    )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

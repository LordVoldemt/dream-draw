import sqlite3
from pathlib import Path

from app.infrastructure.database import Database


def test_schema_initializes_required_tables_and_indexes(tmp_path: Path) -> None:
    database_path = tmp_path / "schema-test.db"
    database = Database(f"sqlite:///{database_path}")
    database.initialize()

    connection = sqlite3.connect(database_path)
    try:
        table_rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        index_rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
    finally:
        connection.close()

    table_names = {row[0] for row in table_rows}
    index_names = {row[0] for row in index_rows}

    assert {
        "users",
        "sms_codes",
        "generation_tasks",
        "works",
        "point_transactions",
        "payment_orders",
        "share_events",
        "favorites",
        "model_providers",
        "model_health_logs",
        "admins",
    }.issubset(table_names)
    assert "idx_generation_tasks_user_id" in index_names


def test_users_phone_is_unique(tmp_path: Path) -> None:
    database_path = tmp_path / "constraint-test.db"
    database = Database(f"sqlite:///{database_path}")
    database.initialize()

    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            INSERT INTO users (nickname, phone, login_type, points_balance, status, created_at, last_login_at)
            VALUES ('A', '13800138006', 'phone_sms', 10, 'active', '2026-05-19T00:00:00+00:00', '2026-05-19T00:00:00+00:00')
            """
        )
        connection.commit()
        try:
            connection.execute(
                """
                INSERT INTO users (nickname, phone, login_type, points_balance, status, created_at, last_login_at)
                VALUES ('B', '13800138006', 'phone_sms', 10, 'active', '2026-05-19T00:00:00+00:00', '2026-05-19T00:00:00+00:00')
                """
            )
            connection.commit()
            duplicate_allowed = True
        except sqlite3.IntegrityError:
            duplicate_allowed = False
    finally:
        connection.close()

    assert duplicate_allowed is False


def test_schema_initialization_upgrades_existing_generation_task_table(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy-schema-test.db"
    connection = sqlite3.connect(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE generation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                prompt TEXT NOT NULL,
                style_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                ratio_id TEXT NOT NULL,
                quality_level TEXT NOT NULL,
                final_points INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()

    database = Database(f"sqlite:///{database_path}")
    database.initialize()

    connection = sqlite3.connect(database_path)
    try:
        column_rows = connection.execute("PRAGMA table_info(generation_tasks)").fetchall()
    finally:
        connection.close()

    column_names = {row[1] for row in column_rows}
    assert {
        "reference_mode",
        "reference_image_count",
        "provider_id",
        "finished_at",
    }.issubset(column_names)

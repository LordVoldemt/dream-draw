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

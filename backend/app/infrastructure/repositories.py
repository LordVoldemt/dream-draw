from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from app.infrastructure.database import Database


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class AuthCodeRecord:
    phone: str
    code: str
    expires_at: str


class AuthCodeRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_code(self, phone: str, code: str, ttl_minutes: int = 5) -> None:
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).replace(
            microsecond=0,
        ).isoformat()
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO sms_codes (phone, code, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(phone) DO UPDATE SET
                    code = excluded.code,
                    expires_at = excluded.expires_at,
                    created_at = excluded.created_at
                """,
                (phone, code, expires_at, utc_now_iso()),
            )
            connection.commit()

    def verify_code(self, phone: str, code: str) -> bool:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT code, expires_at FROM sms_codes WHERE phone = ?",
                (phone,),
            ).fetchone()
            if row is None:
                return False
            if row["code"] != code:
                return False
            if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
                return False
            return True

    def consume_code(self, phone: str) -> None:
        with self.database.connection() as connection:
            connection.execute("DELETE FROM sms_codes WHERE phone = ?", (phone,))
            connection.commit()


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def find_by_id(self, user_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def find_by_phone(self, phone: str) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
            return dict(row) if row else None

    def create_user(self, phone: str, initial_points: int) -> dict[str, Any]:
        created_at = utc_now_iso()
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (
                    nickname, phone, login_type, points_balance, status, created_at, last_login_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("新用户", phone, "phone_sms", initial_points, "active", created_at, created_at),
            )
            user_id = cursor.lastrowid
            connection.commit()
        return self.find_by_id(int(user_id))  # type: ignore[arg-type]

    def update_last_login(self, user_id: int) -> None:
        with self.database.connection() as connection:
            connection.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (utc_now_iso(), user_id),
            )
            connection.commit()

    def adjust_points(self, user_id: int, delta: int) -> int:
        with self.database.connection() as connection:
            connection.execute(
                "UPDATE users SET points_balance = points_balance + ? WHERE id = ?",
                (delta, user_id),
            )
            connection.commit()
        user = self.find_by_id(user_id)
        assert user is not None
        return int(user["points_balance"])

    def update_status(self, user_id: int, status: str) -> None:
        with self.database.connection() as connection:
            connection.execute(
                "UPDATE users SET status = ? WHERE id = ?",
                (status, user_id),
            )
            connection.commit()

    def search(self, keyword: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if keyword:
            clauses.append("(phone LIKE ? OR nickname LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if status:
            clauses.append("status = ?")
            params.append(status)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database.connection() as connection:
            rows = connection.execute(
                f"""
                SELECT id, nickname, phone, login_type, points_balance, status, created_at, last_login_at
                FROM users
                {where_sql}
                ORDER BY id DESC
                """,
                tuple(params),
            ).fetchall()
            return [dict(row) for row in rows]

    def count_all(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS total_count FROM users").fetchone()
            assert row is not None
            return int(row["total_count"])


class PointTransactionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        user_id: int,
        delta: int,
        transaction_type: str,
        reason: str,
        related_task_id: int | None = None,
        related_order_id: int | None = None,
    ) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO point_transactions (
                    user_id, delta, type, reason, related_order_id, related_task_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    delta,
                    transaction_type,
                    reason,
                    related_order_id,
                    related_task_id,
                    utc_now_iso(),
                ),
            )
            connection.commit()

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT id, delta, type, reason, related_order_id, related_task_id, created_at
                FROM point_transactions
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
            return [dict(row) for row in rows]


class GenerationTaskRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        user_id: int,
        prompt: str,
        style_id: str,
        template_id: str,
        ratio_id: str,
        quality_level: str,
        reference_mode: str | None,
        reference_image_count: int,
        final_points: int,
        provider_id: str | None = None,
        status: str = "pending",
    ) -> dict[str, Any]:
        created_at = utc_now_iso()
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO generation_tasks (
                    user_id, status, prompt, style_id, template_id, ratio_id,
                    quality_level, reference_mode, reference_image_count, final_points, provider_id,
                    created_at, finished_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    status,
                    prompt,
                    style_id,
                    template_id,
                    ratio_id,
                    quality_level,
                    reference_mode,
                    reference_image_count,
                    final_points,
                    provider_id,
                    created_at,
                    None,
                ),
            )
            task_id = int(cursor.lastrowid)
            connection.commit()
        task = self.find_by_id(task_id)
        assert task is not None
        return task

    def find_by_id(self, task_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM generation_tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
            return dict(row) if row else None

    def count_active_for_user(self, user_id: int) -> int:
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS active_count
                FROM generation_tasks
                WHERE user_id = ? AND status IN ('pending', 'generating', 'reviewing')
                """,
                (user_id,),
            ).fetchone()
            assert row is not None
            return int(row["active_count"])

    def count_created_today_for_user(self, user_id: int) -> int:
        today_prefix = datetime.now(timezone.utc).date().isoformat()
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total_count
                FROM generation_tasks
                WHERE user_id = ? AND created_at LIKE ?
                """,
                (user_id, f"{today_prefix}%"),
            ).fetchone()
            assert row is not None
            return int(row["total_count"])

    def has_duplicate_prompt_today(self, user_id: int, prompt: str) -> bool:
        today_prefix = datetime.now(timezone.utc).date().isoformat()
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM generation_tasks
                WHERE user_id = ? AND prompt = ? AND created_at LIKE ?
                LIMIT 1
                """,
                (user_id, prompt, f"{today_prefix}%"),
            ).fetchone()
            return row is not None

    def count_global_active(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS active_count
                FROM generation_tasks
                WHERE status IN ('pending', 'generating', 'reviewing')
                """
            ).fetchone()
            assert row is not None
            return int(row["active_count"])

    def update_status(
        self,
        task_id: int,
        status: str,
        provider_id: str | None = None,
    ) -> None:
        finished_at = utc_now_iso() if status in {"success", "failed", "blocked"} else None
        with self.database.connection() as connection:
            connection.execute(
                """
                UPDATE generation_tasks
                SET status = ?, provider_id = COALESCE(?, provider_id), finished_at = COALESCE(?, finished_at)
                WHERE id = ?
                """,
                (status, provider_id, finished_at, task_id),
            )
            connection.commit()


class WorkRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        user_id: int,
        task_id: int,
        image_url: str,
        thumbnail_url: str,
        share_image_url: str,
        review_status: str,
        prompt_snapshot: str,
        style_id: str,
        template_id: str,
        ratio_id: str,
        quality_level: str,
        reference_mode: str | None,
        reference_image_count: int,
        final_points: int,
    ) -> dict[str, Any]:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO works (
                    user_id, task_id, image_url, thumbnail_url, share_image_url,
                    review_status, prompt_snapshot, style_id, template_id, ratio_id,
                    quality_level, reference_mode, reference_image_count, final_points, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    task_id,
                    image_url,
                    thumbnail_url,
                    share_image_url,
                    review_status,
                    prompt_snapshot,
                    style_id,
                    template_id,
                    ratio_id,
                    quality_level,
                    reference_mode,
                    reference_image_count,
                    final_points,
                    utc_now_iso(),
                ),
            )
            work_id = int(cursor.lastrowid)
            connection.commit()
        work = self.find_by_id(work_id)
        assert work is not None
        return work

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM works
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def find_by_id(self, work_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM works WHERE id = ?",
                (work_id,),
            ).fetchone()
            return dict(row) if row else None

    def find_by_task_id(self, task_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM works WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            return dict(row) if row else None

    def count_all(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS total_count FROM works").fetchone()
            assert row is not None
            return int(row["total_count"])


class ShareEventRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, user_id: int, work_id: int, channel: str, share_code: str) -> dict[str, Any]:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO share_events (user_id, work_id, channel, share_code, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, work_id, channel, share_code, utc_now_iso()),
            )
            share_id = int(cursor.lastrowid)
            connection.commit()
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM share_events WHERE id = ?",
                (share_id,),
            ).fetchone()
            assert row is not None
            return dict(row)

    def list_by_user(self, user_id: int) -> list[dict[str, Any]]:
        with self.database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM share_events WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def count_all(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS total_count FROM share_events").fetchone()
            assert row is not None
            return int(row["total_count"])


class FavoriteRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, user_id: int, work_id: int) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO favorites (user_id, work_id, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, work_id, utc_now_iso()),
            )
            connection.commit()

    def remove(self, user_id: int, work_id: int) -> None:
        with self.database.connection() as connection:
            connection.execute(
                "DELETE FROM favorites WHERE user_id = ? AND work_id = ?",
                (user_id, work_id),
            )
            connection.commit()

    def exists(self, user_id: int, work_id: int) -> bool:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT id FROM favorites WHERE user_id = ? AND work_id = ? LIMIT 1",
                (user_id, work_id),
            ).fetchone()
            return row is not None

    def list_work_ids_by_user(self, user_id: int) -> list[int]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT work_id
                FROM favorites
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
            return [int(row["work_id"]) for row in rows]

    def count_by_user(self, user_id: int) -> int:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total_count FROM favorites WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            assert row is not None
            return int(row["total_count"])

    def count_all(self) -> int:
        with self.database.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS total_count FROM favorites").fetchone()
            assert row is not None
            return int(row["total_count"])


class PaymentOrderRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, user_id: int, channel: str, amount: float, points_amount: int) -> dict[str, Any]:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO payment_orders (user_id, channel, amount, points_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, channel, amount, points_amount, "pending", utc_now_iso()),
            )
            order_id = int(cursor.lastrowid)
            connection.commit()
        order = self.find_by_id(order_id)
        assert order is not None
        return order

    def find_by_id(self, order_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM payment_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
            return dict(row) if row else None

    def update_status(self, order_id: int, status: str) -> None:
        with self.database.connection() as connection:
            connection.execute(
                "UPDATE payment_orders SET status = ? WHERE id = ?",
                (status, order_id),
            )
            connection.commit()


class AdminRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def ensure_default_admin(self) -> None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT id FROM admins WHERE account = 'admin'").fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO admins (account, password_hash, status, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    ("admin", "admin123", "active", utc_now_iso()),
                )
                connection.commit()

    def find_by_account(self, account: str) -> dict[str, Any] | None:
        self.ensure_default_admin()
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM admins WHERE account = ?",
                (account,),
            ).fetchone()
            return dict(row) if row else None


class ModelProviderRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def ensure_seed_provider(self) -> None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT id FROM model_providers WHERE provider_id = 'system-default-provider'"
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO model_providers (
                        provider_id, provider_name, base_url, api_key_ref, model_name,
                        api_mode, capabilities, priority, status, timeout_seconds,
                        qps_limit, cost_level, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "system-default-provider",
                        "System Default Provider",
                        "https://api.default-provider.local/v1",
                        "env:SYSTEM_DEFAULT_PROVIDER_KEY",
                        "gufeng-default-v1",
                        "openai_compatible",
                        "text_to_image,reference_image",
                        999,
                        "healthy",
                        60,
                        5,
                        "medium",
                        utc_now_iso(),
                    ),
                )
                connection.commit()

    def list_all(self) -> list[dict[str, Any]]:
        self.ensure_seed_provider()
        with self.database.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM model_providers ORDER BY priority ASC, id ASC"
            ).fetchall()
            return [dict(row) for row in rows]

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO model_providers (
                    provider_id, provider_name, base_url, api_key_ref, model_name,
                    api_mode, capabilities, priority, status, timeout_seconds,
                    qps_limit, cost_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["provider_id"],
                    payload["provider_name"],
                    payload["base_url"],
                    payload.get("api_key_ref"),
                    payload["model_name"],
                    payload.get("api_mode", "openai_compatible"),
                    ",".join(payload.get("capabilities", [])),
                    payload.get("priority", 100),
                    payload.get("status", "healthy"),
                    payload.get("timeout_seconds", 60),
                    payload.get("qps_limit", 5),
                    payload.get("cost_level", "medium"),
                    utc_now_iso(),
                ),
            )
            provider_db_id = int(cursor.lastrowid)
            connection.commit()
        return self.find_by_db_id(provider_db_id) or payload

    def find_by_db_id(self, provider_db_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM model_providers WHERE id = ?",
                (provider_db_id,),
            ).fetchone()
            return dict(row) if row else None

    def find_by_provider_id(self, provider_id: str) -> dict[str, Any] | None:
        self.ensure_seed_provider()
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT id, provider_id, provider_name, base_url, api_key_ref, model_name,
                       api_mode, capabilities, priority, status, timeout_seconds,
                       qps_limit, cost_level, created_at
                FROM model_providers
                WHERE provider_id = ?
                """,
                (provider_id,),
            ).fetchone()
            return dict(row) if row else None

    def update(self, provider_db_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.find_by_db_id(provider_db_id)
        assert current is not None
        merged = {**current, **payload}
        with self.database.connection() as connection:
            connection.execute(
                """
                UPDATE model_providers
                SET provider_name = ?, base_url = ?, api_key_ref = ?, model_name = ?,
                    api_mode = ?, capabilities = ?, priority = ?, status = ?,
                    timeout_seconds = ?, qps_limit = ?, cost_level = ?
                WHERE id = ?
                """,
                (
                    merged["provider_name"],
                    merged["base_url"],
                    merged.get("api_key_ref"),
                    merged["model_name"],
                    merged.get("api_mode", "openai_compatible"),
                    ",".join(merged.get("capabilities", "").split(","))
                    if isinstance(merged.get("capabilities"), str)
                    else ",".join(merged.get("capabilities", [])),
                    merged.get("priority", 100),
                    merged.get("status", "healthy"),
                    merged.get("timeout_seconds", 60),
                    merged.get("qps_limit", 5),
                    merged.get("cost_level", "medium"),
                    provider_db_id,
                ),
            )
            connection.commit()
        updated = self.find_by_db_id(provider_db_id)
        assert updated is not None
        return updated

    def update_status(self, provider_db_id: int, status: str) -> dict[str, Any]:
        return self.update(provider_db_id, {"status": status})

    def select_provider_for_generation(self) -> dict[str, Any] | None:
        providers = self.list_all()
        eligible = [provider for provider in providers if provider["provider_name"] == "text_to_image"]
        if not eligible:
            return None
        return eligible[0]


class ModelHealthLogRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(
        self,
        provider_internal_id: int,
        status: str,
        success_rate: float,
        average_latency_ms: float,
        timeout_count: int,
        failure_count: int,
        blocked_rate: float,
        queue_depth: int,
    ) -> None:
        with self.database.connection() as connection:
            connection.execute(
                """
                INSERT INTO model_health_logs (
                    provider_id, status, success_rate, average_latency_ms,
                    timeout_count, failure_count, blocked_rate, queue_depth, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider_internal_id,
                    status,
                    success_rate,
                    average_latency_ms,
                    timeout_count,
                    failure_count,
                    blocked_rate,
                    queue_depth,
                    utc_now_iso(),
                ),
            )
            connection.commit()

    def latest_metrics(self) -> list[dict[str, Any]]:
        with self.database.connection() as connection:
            rows = connection.execute(
                """
                SELECT mp.id AS provider_db_id, mp.provider_id, mp.provider_name, mp.model_name,
                       COALESCE(mhl.status, mp.status) AS status,
                       COALESCE(mhl.success_rate, 0) AS success_rate,
                       COALESCE(mhl.average_latency_ms, 0) AS average_latency_ms,
                       COALESCE(mhl.timeout_count, 0) AS timeout_count,
                       COALESCE(mhl.failure_count, 0) AS failure_count,
                       COALESCE(mhl.blocked_rate, 0) AS blocked_rate,
                       COALESCE(mhl.queue_depth, 0) AS queue_depth
                FROM model_providers mp
                LEFT JOIN model_health_logs mhl
                    ON mhl.id = (
                        SELECT id FROM model_health_logs
                        WHERE provider_id = mp.id
                        ORDER BY id DESC LIMIT 1
                    )
                ORDER BY mp.priority ASC, mp.id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]


class UserReadRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def profile(self, user_id: int) -> dict[str, Any] | None:
        with self.database.connection() as connection:
            row = connection.execute(
                """
                SELECT id, nickname, phone, login_type, points_balance, status, created_at, last_login_at
                FROM users WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
            return dict(row) if row else None

    def admin_detail(self, user_id: int) -> dict[str, Any] | None:
        profile = self.profile(user_id)
        if profile is None:
            return None
        profile["masked_phone"] = f"{profile['phone'][:3]}****{profile['phone'][-4:]}"
        return profile

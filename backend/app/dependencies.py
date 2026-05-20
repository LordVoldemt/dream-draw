from __future__ import annotations

from fastapi import Depends, Header, Request

from app.core.config import AppSettings, get_settings
from app.core.errors import AppError
from app.infrastructure.database import Database
from app.infrastructure.repositories import (
    AdminRepository,
    AuthCodeRepository,
    FavoriteRepository,
    GenerationTaskRepository,
    ModelHealthLogRepository,
    ModelProviderRepository,
    PaymentOrderRepository,
    PointTransactionRepository,
    ShareEventRepository,
    UserReadRepository,
    UserRepository,
    WorkRepository,
)
from app.shared.auth import admin_session_manager, session_manager


def get_app_settings(request: Request) -> AppSettings:
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        return get_settings()
    return settings


def get_database(settings: AppSettings = Depends(get_app_settings)) -> Database:
    database = Database(settings.database.url)
    database.initialize()
    return database


def get_auth_code_repository(database: Database = Depends(get_database)) -> AuthCodeRepository:
    return AuthCodeRepository(database)


def get_user_repository(database: Database = Depends(get_database)) -> UserRepository:
    return UserRepository(database)


def get_user_read_repository(database: Database = Depends(get_database)) -> UserReadRepository:
    return UserReadRepository(database)


def get_point_transaction_repository(
    database: Database = Depends(get_database),
) -> PointTransactionRepository:
    return PointTransactionRepository(database)


def get_generation_task_repository(
    database: Database = Depends(get_database),
) -> GenerationTaskRepository:
    return GenerationTaskRepository(database)


def get_work_repository(database: Database = Depends(get_database)) -> WorkRepository:
    return WorkRepository(database)


def get_share_event_repository(database: Database = Depends(get_database)) -> ShareEventRepository:
    return ShareEventRepository(database)


def get_favorite_repository(database: Database = Depends(get_database)) -> FavoriteRepository:
    return FavoriteRepository(database)


def get_payment_order_repository(database: Database = Depends(get_database)) -> PaymentOrderRepository:
    return PaymentOrderRepository(database)


def get_admin_repository(database: Database = Depends(get_database)) -> AdminRepository:
    return AdminRepository(database)


def get_model_provider_repository(
    database: Database = Depends(get_database),
) -> ModelProviderRepository:
    return ModelProviderRepository(database)


def get_model_health_log_repository(
    database: Database = Depends(get_database),
) -> ModelHealthLogRepository:
    return ModelHealthLogRepository(database)


def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("unauthorized", "请先登录后再继续", status_code=401)
    token = authorization.removeprefix("Bearer ").strip()
    user_id = session_manager.get_user_id(token)
    if user_id is None:
        raise AppError("unauthorized", "登录已失效，请重新登录", status_code=401)
    return user_id


def get_current_admin_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("unauthorized", "请先登录管理员账号", status_code=401)
    token = authorization.removeprefix("Bearer ").strip()
    admin_id = admin_session_manager.get_user_id(token)
    if admin_id is None:
        raise AppError("unauthorized", "管理员登录已失效，请重新登录", status_code=401)
    return admin_id

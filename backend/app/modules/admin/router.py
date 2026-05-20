from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query

from app.core.errors import AppError
from app.dependencies import (
    get_admin_repository,
    get_current_admin_id,
    get_favorite_repository,
    get_generation_task_repository,
    get_model_health_log_repository,
    get_point_transaction_repository,
    get_share_event_repository,
    get_user_read_repository,
    get_user_repository,
    get_work_repository,
)
from app.infrastructure.repositories import (
    AdminRepository,
    FavoriteRepository,
    GenerationTaskRepository,
    ModelHealthLogRepository,
    PointTransactionRepository,
    ShareEventRepository,
    UserReadRepository,
    UserRepository,
    WorkRepository,
)
from app.shared.auth import admin_session_manager

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "admin"}


class AdminLoginRequest(BaseModel):
    account: str
    password: str


class AdjustUserPointsRequest(BaseModel):
    delta: int
    reason: str
    confirm: bool


class UpdateUserStatusRequest(BaseModel):
    status: str
    reason: str
    confirm: bool


@router.post("/login")
async def admin_login(
    payload: AdminLoginRequest,
    admins: AdminRepository = Depends(get_admin_repository),
) -> dict:
    admin = admins.find_by_account(payload.account)
    if admin is None or admin["password_hash"] != payload.password:
        raise AppError("invalid_credentials", "账号或密码错误", status_code=401)
    if admin["status"] != "active":
        raise AppError("admin_disabled", "管理员账号已禁用", status_code=403)
    token = admin_session_manager.issue_user_token(int(admin["id"]))
    return {"token": token, "admin": {"id": admin["id"], "account": admin["account"]}}


@router.get("/overview")
async def admin_overview(
    _admin_id: int = Depends(get_current_admin_id),
    users: UserRepository = Depends(get_user_repository),
    tasks: GenerationTaskRepository = Depends(get_generation_task_repository),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
    shares: ShareEventRepository = Depends(get_share_event_repository),
    monitoring: ModelHealthLogRepository = Depends(get_model_health_log_repository),
) -> dict:
    provider_metrics = monitoring.latest_metrics()
    provider_summary = {
        "healthy": len([item for item in provider_metrics if item["status"] == "healthy"]),
        "degraded": len([item for item in provider_metrics if item["status"] == "degraded"]),
        "maintenance": len([item for item in provider_metrics if item["status"] == "maintenance"]),
        "unavailable": len([item for item in provider_metrics if item["status"] == "unavailable"]),
    }
    return {
        "overview": {
            "users_total": users.count_all(),
            "works_total": works.count_all(),
            "active_tasks_total": tasks.count_global_active(),
            "favorites_total": favorites.count_all(),
            "shares_total": shares.count_all(),
            "provider_summary": provider_summary,
            "providers": provider_metrics,
        }
    }


@router.get("/users")
async def admin_list_users(
    _admin_id: int = Depends(get_current_admin_id),
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    users: UserRepository = Depends(get_user_repository),
) -> dict:
    items = users.search(keyword=keyword, status=status)
    for item in items:
        item["masked_phone"] = f"{item['phone'][:3]}****{item['phone'][-4:]}"
    return {"users": items}


@router.get("/users/{user_id}")
async def admin_get_user_detail(
    user_id: int,
    _admin_id: int = Depends(get_current_admin_id),
    users: UserReadRepository = Depends(get_user_read_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
) -> dict:
    detail = users.admin_detail(user_id)
    if detail is None:
        raise AppError("user_not_found", "用户不存在", status_code=404)
    return {
        "user": detail,
        "points_transactions": transactions.list_by_user(user_id),
    }


@router.patch("/users/{user_id}/points")
async def admin_adjust_user_points(
    user_id: int,
    payload: AdjustUserPointsRequest,
    _admin_id: int = Depends(get_current_admin_id),
    users: UserRepository = Depends(get_user_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
) -> dict:
    if not payload.confirm or not payload.reason.strip():
        raise AppError("confirmation_required", "调整积分需要填写原因并二次确认", status_code=422)
    user = users.find_by_id(user_id)
    if user is None:
        raise AppError("user_not_found", "用户不存在", status_code=404)
    balance = users.adjust_points(user_id, payload.delta)
    transactions.create(
        user_id=user_id,
        delta=payload.delta,
        transaction_type="admin_adjustment",
        reason=payload.reason,
    )
    return {"user_id": user_id, "points_balance": balance}


@router.patch("/users/{user_id}/status")
async def admin_update_user_status(
    user_id: int,
    payload: UpdateUserStatusRequest,
    _admin_id: int = Depends(get_current_admin_id),
    users: UserRepository = Depends(get_user_repository),
) -> dict:
    if not payload.confirm or not payload.reason.strip():
        raise AppError("confirmation_required", "更新状态需要填写原因并二次确认", status_code=422)
    user = users.find_by_id(user_id)
    if user is None:
        raise AppError("user_not_found", "用户不存在", status_code=404)
    users.update_status(user_id, payload.status)
    return {"user_id": user_id, "status": payload.status}

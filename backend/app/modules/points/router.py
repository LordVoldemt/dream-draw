from fastapi import APIRouter, Depends

from app.dependencies import (
    get_current_user_id,
    get_point_transaction_repository,
    get_user_read_repository,
)
from app.infrastructure.repositories import PointTransactionRepository, UserReadRepository

router = APIRouter(prefix="/points", tags=["points"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "points"}


@router.get("")
async def get_points_summary(
    user_id: int = Depends(get_current_user_id),
    users: UserReadRepository = Depends(get_user_read_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
) -> dict:
    profile = users.profile(user_id)
    assert profile is not None
    return {
        "balance": profile["points_balance"],
        "transactions": transactions.list_by_user(user_id),
    }

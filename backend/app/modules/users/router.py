from fastapi import APIRouter, Depends

from app.dependencies import get_current_user_id, get_user_read_repository
from app.infrastructure.repositories import UserReadRepository

router = APIRouter(prefix="/user", tags=["users"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "users"}


@router.get("/profile")
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    users: UserReadRepository = Depends(get_user_read_repository),
) -> dict:
    profile = users.profile(user_id)
    if profile is None:
        return {"profile": None}
    return {"profile": profile}

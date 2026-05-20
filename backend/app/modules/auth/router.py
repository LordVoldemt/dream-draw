from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.dependencies import (
    get_auth_code_repository,
    get_point_transaction_repository,
    get_user_repository,
)
from app.infrastructure.repositories import (
    AuthCodeRepository,
    PointTransactionRepository,
    UserRepository,
)
from app.shared.auth import session_manager

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "auth"}


class SendCodeRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=11)


class LoginRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=11)
    code: str = Field(min_length=4, max_length=6)


@router.post("/sms/send-code")
async def send_sms_code(
    payload: SendCodeRequest,
    repository: AuthCodeRepository = Depends(get_auth_code_repository),
) -> dict:
    if not payload.phone.isdigit():
        raise AppError("invalid_phone", "手机号格式不正确", status_code=422)

    code = "123456"
    repository.save_code(payload.phone, code)
    return {"success": True, "cooldown_seconds": 60, "mock_code": code}


@router.post("/login")
async def login_by_sms(
    payload: LoginRequest,
    auth_codes: AuthCodeRepository = Depends(get_auth_code_repository),
    users: UserRepository = Depends(get_user_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
) -> dict:
    if not auth_codes.verify_code(payload.phone, payload.code):
        raise AppError("invalid_code", "验证码错误或已过期", status_code=422)

    user = users.find_by_phone(payload.phone)
    is_first_login = user is None
    if is_first_login:
        user = users.create_user(payload.phone, initial_points=10)
        transactions.create(
            user_id=int(user["id"]),
            delta=10,
            transaction_type="signup_bonus",
            reason="首次登录赠送 10 点积分",
        )
    else:
        users.update_last_login(int(user["id"]))
        user = users.find_by_phone(payload.phone)

    auth_codes.consume_code(payload.phone)
    assert user is not None
    token = session_manager.issue_user_token(int(user["id"]))
    return {
        "token": token,
        "is_first_login": is_first_login,
        "user": {
            "id": user["id"],
            "phone": user["phone"],
            "nickname": user["nickname"],
            "points_balance": user["points_balance"],
            "status": user["status"],
        },
    }

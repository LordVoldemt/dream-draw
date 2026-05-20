from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.dependencies import (
    get_current_user_id,
    get_payment_order_repository,
    get_point_transaction_repository,
    get_user_repository,
)
from app.infrastructure.repositories import (
    PaymentOrderRepository,
    PointTransactionRepository,
    UserRepository,
)

router = APIRouter(prefix="/pay", tags=["payments"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "payments"}


PACKAGES = {
    "pkg_30": {"points": 30, "amount": 9.9},
    "pkg_100": {"points": 100, "amount": 29.9},
    "pkg_300": {"points": 300, "amount": 69.9},
}


class CreateOrderRequest(BaseModel):
    package_id: str
    channel: str


class PaymentCallbackRequest(BaseModel):
    order_id: int
    status: str


@router.post("/orders")
async def create_payment_order(
    payload: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    orders: PaymentOrderRepository = Depends(get_payment_order_repository),
) -> dict:
    package = PACKAGES.get(payload.package_id)
    if package is None:
        raise AppError("invalid_package", "充值套餐不存在", status_code=422)
    if payload.channel not in {"wechat", "alipay"}:
        raise AppError("invalid_channel", "支付渠道不支持", status_code=422)
    order = orders.create(
        user_id=user_id,
        channel=payload.channel,
        amount=package["amount"],
        points_amount=package["points"],
    )
    return {"order": order}


@router.post("/callback/{channel}")
async def handle_payment_callback(
    channel: str,
    payload: PaymentCallbackRequest,
    orders: PaymentOrderRepository = Depends(get_payment_order_repository),
    users: UserRepository = Depends(get_user_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
) -> dict:
    if channel not in {"wechat", "alipay"}:
        raise AppError("invalid_channel", "支付渠道不支持", status_code=422)
    order = orders.find_by_id(payload.order_id)
    if order is None:
        raise AppError("order_not_found", "订单不存在", status_code=404)
    if order["channel"] != channel:
        raise AppError("channel_mismatch", "回调渠道不匹配", status_code=409)
    if order["status"] == "paid":
        return {"order": order, "duplicate": True}
    if payload.status != "success":
        orders.update_status(payload.order_id, "failed")
        return {"order": orders.find_by_id(payload.order_id)}
    orders.update_status(payload.order_id, "paid")
    users.adjust_points(int(order["user_id"]), int(order["points_amount"]))
    transactions.create(
        user_id=int(order["user_id"]),
        delta=int(order["points_amount"]),
        transaction_type="recharge",
        reason=f"{channel} 支付充值到账",
        related_order_id=int(order["id"]),
    )
    return {"order": orders.find_by_id(payload.order_id), "duplicate": False}

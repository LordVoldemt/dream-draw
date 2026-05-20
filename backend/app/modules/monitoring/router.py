from fastapi import APIRouter, Depends

from app.dependencies import get_current_admin_id, get_model_health_log_repository
from app.infrastructure.repositories import ModelHealthLogRepository

router = APIRouter(prefix="/admin/model-monitoring", tags=["monitoring"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "monitoring"}


@router.get("")
async def get_model_monitoring(
    _admin_id: int = Depends(get_current_admin_id),
    monitoring: ModelHealthLogRepository = Depends(get_model_health_log_repository),
) -> dict:
    return {"monitoring": monitoring.latest_metrics()}

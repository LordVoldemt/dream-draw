from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from app.core.errors import AppError
from app.dependencies import (
    get_current_admin_id,
    get_model_provider_repository,
)
from app.infrastructure.repositories import ModelProviderRepository

router = APIRouter(prefix="/admin/model-providers", tags=["model-providers"])


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "model-providers"}


class CreateModelProviderRequest(BaseModel):
    provider_id: str
    provider_name: str
    base_url: str
    api_key_ref: str | None = None
    model_name: str
    api_mode: str = "openai_compatible"
    capabilities: list[str] = Field(default_factory=list)
    priority: int = 100
    status: str = "healthy"
    timeout_seconds: int = 60
    qps_limit: int = 5
    cost_level: str = "medium"


class UpdateModelProviderRequest(CreateModelProviderRequest):
    pass


class UpdateProviderStatusRequest(BaseModel):
    status: str


@router.get("")
async def list_model_providers(
    _admin_id: int = Depends(get_current_admin_id),
    providers: ModelProviderRepository = Depends(get_model_provider_repository),
) -> dict:
    return {"providers": providers.list_all()}


@router.post("")
async def create_model_provider(
    payload: CreateModelProviderRequest,
    _admin_id: int = Depends(get_current_admin_id),
    providers: ModelProviderRepository = Depends(get_model_provider_repository),
) -> dict:
    if payload.api_mode != "openai_compatible":
        raise AppError("invalid_api_mode", "当前仅支持 openai_compatible", status_code=422)
    provider = providers.create(payload.model_dump())
    return {"provider": provider}


@router.patch("/{provider_id}")
async def update_model_provider(
    provider_id: int,
    payload: UpdateModelProviderRequest,
    _admin_id: int = Depends(get_current_admin_id),
    providers: ModelProviderRepository = Depends(get_model_provider_repository),
) -> dict:
    if payload.api_mode != "openai_compatible":
        raise AppError("invalid_api_mode", "当前仅支持 openai_compatible", status_code=422)
    provider = providers.update(provider_id, payload.model_dump())
    return {"provider": provider}


@router.patch("/{provider_id}/status")
async def update_model_provider_status(
    provider_id: int,
    payload: UpdateProviderStatusRequest,
    _admin_id: int = Depends(get_current_admin_id),
    providers: ModelProviderRepository = Depends(get_model_provider_repository),
) -> dict:
    provider = providers.update_status(provider_id, payload.status)
    return {"provider": provider}

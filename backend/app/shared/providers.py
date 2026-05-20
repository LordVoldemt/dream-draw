from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


ProviderStatus = Literal["healthy", "degraded", "unavailable", "maintenance"]


class ObjectStorageConfig(BaseModel):
    endpoint: str = "http://127.0.0.1:9000"
    bucket: str = "dream-draw"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    secure: bool = False


class RedisConfig(BaseModel):
    url: str = "redis://127.0.0.1:6379/0"


class DatabaseConfig(BaseModel):
    url: str = "sqlite:///dream_draw.db"


class SmsProviderConfig(BaseModel):
    provider_name: str = "mock-sms"
    endpoint: HttpUrl | None = None
    api_key: str = ""
    sign_name: str = "绘梦"


class PaymentChannelConfig(BaseModel):
    app_id: str = ""
    merchant_id: str = ""
    notify_url: HttpUrl | None = None


class PaymentConfig(BaseModel):
    wechat: PaymentChannelConfig = Field(default_factory=PaymentChannelConfig)
    alipay: PaymentChannelConfig = Field(default_factory=PaymentChannelConfig)


class OpenAICompatibleProviderConfig(BaseModel):
    provider_id: str
    provider_name: str
    base_url: HttpUrl
    api_key: str
    model_name: str
    api_mode: Literal["openai_compatible"] = "openai_compatible"
    capabilities: list[str] = Field(default_factory=list)
    priority: int = 100
    status: ProviderStatus = "healthy"
    timeout_seconds: int = 60
    qps_limit: int = 5
    cost_level: Literal["low", "medium", "high"] = "medium"
    is_default: bool = False
    is_fallback: bool = False


class ModelProviderRegistry(BaseModel):
    providers: list[OpenAICompatibleProviderConfig] = Field(default_factory=list)

    def sorted_active_providers(self) -> list[OpenAICompatibleProviderConfig]:
        return sorted(
            [
                provider
                for provider in self.providers
                if provider.status in {"healthy", "degraded"}
            ],
            key=lambda provider: provider.priority,
        )


class ImageGenerationRequest(BaseModel):
    prompt: str
    style_id: str
    template_id: str
    ratio_id: str
    quality_level: str
    reference_image_urls: list[HttpUrl] = Field(default_factory=list)


class GeneratedImageResult(BaseModel):
    image_url: HttpUrl
    provider_id: str
    raw_response: dict


class BaseImageProviderAdapter(ABC):
    def __init__(self, config: OpenAICompatibleProviderConfig) -> None:
        self.config = config

    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> GeneratedImageResult:
        """调用底层模型并返回统一结果。"""

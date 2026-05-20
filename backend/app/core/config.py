from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.providers import (
    DatabaseConfig,
    ModelProviderRegistry,
    ObjectStorageConfig,
    PaymentConfig,
    RedisConfig,
    SmsProviderConfig,
)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DREAM_DRAW_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "绘梦 API"
    app_version: str = "0.1.0"
    environment: str = "development"
    object_storage: ObjectStorageConfig = Field(default_factory=ObjectStorageConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    sms: SmsProviderConfig = Field(default_factory=SmsProviderConfig)
    payment: PaymentConfig = Field(default_factory=PaymentConfig)
    model_providers: ModelProviderRegistry = Field(default_factory=ModelProviderRegistry)

    @classmethod
    def from_env(cls, overrides: dict[str, Any] | None = None) -> "AppSettings":
        payload = overrides.copy() if overrides else {}
        if "model_providers" in payload and isinstance(payload["model_providers"], str):
            payload["model_providers"] = ModelProviderRegistry(
                providers=json.loads(payload["model_providers"]),
            )
        elif "model_providers" in payload and isinstance(payload["model_providers"], list):
            payload["model_providers"] = ModelProviderRegistry(
                providers=payload["model_providers"],
            )
        return cls(**payload)


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

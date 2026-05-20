import pytest
from pydantic import ValidationError

from app.shared.providers import ModelProviderRegistry, OpenAICompatibleProviderConfig


def test_provider_registry_sorts_active_providers_by_priority() -> None:
    registry = ModelProviderRegistry(
        providers=[
            OpenAICompatibleProviderConfig(
                provider_id="fallback",
                provider_name="Fallback",
                base_url="https://fallback.example.com/v1",
                api_key="secret",
                model_name="fallback-image",
                priority=20,
                status="degraded",
            ),
            OpenAICompatibleProviderConfig(
                provider_id="primary",
                provider_name="Primary",
                base_url="https://primary.example.com/v1",
                api_key="secret",
                model_name="primary-image",
                priority=10,
                status="healthy",
            ),
            OpenAICompatibleProviderConfig(
                provider_id="offline",
                provider_name="Offline",
                base_url="https://offline.example.com/v1",
                api_key="secret",
                model_name="offline-image",
                priority=1,
                status="unavailable",
            ),
        ]
    )

    assert [provider.provider_id for provider in registry.sorted_active_providers()] == [
        "primary",
        "fallback",
    ]


def test_provider_schema_rejects_non_openai_compatible_mode() -> None:
    with pytest.raises(ValidationError):
        OpenAICompatibleProviderConfig(
            provider_id="provider-1",
            provider_name="Broken",
            base_url="https://api.example.com/v1",
            api_key="secret",
            model_name="broken-model",
            api_mode="custom_mode",
        )

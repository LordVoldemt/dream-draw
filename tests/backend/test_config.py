from app.core.config import AppSettings


def test_settings_parse_nested_infrastructure_config() -> None:
    settings = AppSettings.from_env(
        {
            "object_storage": {
                "endpoint": "https://minio.example.com",
                "bucket": "guofeng-assets",
                "access_key": "access",
                "secret_key": "secret",
                "secure": True,
            },
            "redis": {"url": "redis://127.0.0.1:6379/5"},
            "database": {"url": "postgresql://demo:demo@localhost:5432/dream_draw"},
        }
    )

    assert settings.object_storage.bucket == "guofeng-assets"
    assert settings.object_storage.secure is True
    assert settings.redis.url.endswith("/5")
    assert settings.database.url.startswith("postgresql://")


def test_settings_parse_openai_compatible_provider_registry() -> None:
    settings = AppSettings.from_env(
        {
            "model_providers": [
                {
                    "provider_id": "provider-primary",
                    "provider_name": "Primary Provider",
                    "base_url": "https://api.example.com/v1",
                    "api_key": "secret",
                    "model_name": "gufeng-image-1",
                    "api_mode": "openai_compatible",
                    "capabilities": ["text_to_image"],
                    "priority": 10,
                    "status": "healthy",
                    "timeout_seconds": 45,
                    "qps_limit": 12,
                    "cost_level": "medium",
                    "is_default": True,
                }
            ]
        }
    )

    provider = settings.model_providers.providers[0]
    assert provider.provider_id == "provider-primary"
    assert provider.api_mode == "openai_compatible"
    assert provider.is_default is True

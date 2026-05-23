import pytest

from app.core.errors import AppError
from app.services.prompt_polisher import (
    build_chat_completion_endpoint,
    extract_polished_prompt,
    resolve_prompt_polish_api_key,
)


def test_chat_completion_endpoint_does_not_duplicate_v1_suffix() -> None:
    assert (
        build_chat_completion_endpoint({"base_url": "https://chat-provider.example.com/v1"})
        == "https://chat-provider.example.com/v1/chat/completions"
    )
    assert (
        build_chat_completion_endpoint({"base_url": "https://chat-provider.example.com"})
        == "https://chat-provider.example.com/v1/chat/completions"
    )


def test_extract_polished_prompt_rejects_empty_provider_content() -> None:
    with pytest.raises(AppError) as exc_info:
        extract_polished_prompt({"choices": [{"message": {"content": "   "}}]})

    assert exc_info.value.code == "prompt_polish_invalid_response"


def test_resolve_prompt_polish_api_key_supports_env_references(monkeypatch) -> None:
    monkeypatch.setenv("CHAT_PROVIDER_KEY", "sk-from-env")

    assert resolve_prompt_polish_api_key({"api_key_ref": "env:CHAT_PROVIDER_KEY"}) == "sk-from-env"

    with pytest.raises(AppError) as exc_info:
        resolve_prompt_polish_api_key({"api_key_ref": "env:MISSING_CHAT_PROVIDER_KEY"})

    assert exc_info.value.code == "prompt_polish_provider_invalid"

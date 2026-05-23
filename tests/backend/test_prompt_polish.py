from pathlib import Path
from typing import Any

import httpx
from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'prompt-polish.db'}",
            }
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str = "13800138070") -> dict[str, Any]:
    code_response = client.post("/api/auth/sms/send-code", json={"phone": phone})
    assert code_response.status_code == 200
    code = code_response.json()["mock_code"]

    login_response = client.post("/api/auth/login", json={"phone": phone, "code": code})
    assert login_response.status_code == 200
    return login_response.json()


def login_admin(client: TestClient) -> str:
    response = client.post("/api/admin/login", json={"account": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["token"]


def create_chat_provider(client: TestClient) -> None:
    admin_headers = {"Authorization": f"Bearer {login_admin(client)}"}
    response = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "chat",
            "provider_name": "Prompt Polish Chat",
            "base_url": "https://chat-provider.example.com",
            "api_key_ref": "sk-chat-test",
            "model_name": "gpt-4o-mini",
            "api_mode": "openai_compatible",
            "capabilities": ["text"],
            "priority": 1,
            "status": "healthy",
            "timeout_seconds": 30,
            "qps_limit": 5,
            "cost_level": "low",
        },
    )
    assert response.status_code == 200


def test_prompt_polish_calls_chat_provider_and_returns_expanded_prompt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client = create_test_client(tmp_path)
    create_chat_provider(client)
    user = login_user(client)
    calls: list[dict[str, Any]] = []

    def fake_post(url: str, **kwargs):
        calls.append({"url": url, **kwargs})
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "盛唐贵族少女，金色步摇，红色齐胸襦裙，端庄华贵，柔和宫灯光影，精致国风角色设定图"
                        }
                    }
                ]
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    response = client.post(
        "/api/prompts/polish",
        headers={"Authorization": f"Bearer {user['token']}"},
        json={"prompt": "盛唐少女"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "prompt": "盛唐少女",
        "polished_prompt": "盛唐贵族少女，金色步摇，红色齐胸襦裙，端庄华贵，柔和宫灯光影，精致国风角色设定图",
    }
    assert calls[0]["url"] == "https://chat-provider.example.com/v1/chat/completions"
    assert calls[0]["headers"]["Authorization"] == "Bearer sk-chat-test"
    assert calls[0]["json"]["model"] == "gpt-4o-mini"
    assert calls[0]["json"]["messages"][0]["role"] == "system"
    assert calls[0]["json"]["messages"][1]["content"] == "盛唐少女"


def test_prompt_polish_reports_missing_chat_provider(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138071")

    response = client.post(
        "/api/prompts/polish",
        headers={"Authorization": f"Bearer {user['token']}"},
        json={"prompt": "新中式冷艳女性"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "prompt_polish_provider_not_found"

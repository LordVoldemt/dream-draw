from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'dream-draw-guardrails-test.db'}",
            }
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str) -> dict:
    code = client.post("/api/auth/sms/send-code", json={"phone": phone}).json()["mock_code"]
    return client.post("/api/auth/login", json={"phone": phone, "code": code}).json()


def test_guest_cannot_generate(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    response = client.post(
        "/api/generate/tasks",
        json={
            "prompt": "游客提交生成",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert response.status_code == 401


def test_duplicate_prompt_is_blocked(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138204")
    headers = {"Authorization": f"Bearer {user['token']}", "x-forwarded-for": "10.0.0.4"}
    payload = {
        "prompt": "重复 prompt 检查",
        "ratio_id": "ratio_square_1_1",
        "style_id": "style_han_dynasty",
        "template_id": "tpl_oc_avatar",
        "quality_level": "standard",
        "reference_image_urls": [],
    }

    first_response = client.post("/api/generate/tasks", headers=headers, json=payload)
    duplicate_response = client.post("/api/generate/tasks", headers=headers, json=payload)

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409


def test_daily_limit_blocks_after_twenty_requests(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138205")
    headers = {"Authorization": f"Bearer {user['token']}", "x-forwarded-for": "10.0.0.5"}

    for index in range(10):
        recharge = client.post(
            "/api/pay/orders",
            headers=headers,
            json={"package_id": "pkg_300", "channel": "wechat"},
        )
        order_id = recharge.json()["order"]["id"]
        client.post("/api/pay/callback/wechat", json={"order_id": order_id, "status": "success"})

        request_headers_first = {
            "Authorization": f"Bearer {user['token']}",
            "x-forwarded-for": f"10.0.{index}.5",
        }
        request_headers_second = {
            "Authorization": f"Bearer {user['token']}",
            "x-forwarded-for": f"10.0.{index}.6",
        }

        first = client.post(
            "/api/generate/tasks",
            headers=request_headers_first,
            json={
                "prompt": f"每日限流测试 A-{index}",
                "ratio_id": "ratio_square_1_1",
                "style_id": "style_han_dynasty",
                "template_id": "tpl_oc_avatar",
                "quality_level": "standard",
                "reference_image_urls": [],
            },
        )
        second = client.post(
            "/api/generate/tasks",
            headers=request_headers_second,
            json={
                "prompt": f"每日限流测试 B-{index}",
                "ratio_id": "ratio_square_1_1",
                "style_id": "style_han_dynasty",
                "template_id": "tpl_oc_avatar",
                "quality_level": "standard",
                "reference_image_urls": [],
            },
        )
        assert first.status_code == 200
        assert second.status_code == 200

    blocked = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "每日限流测试 最后一条",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert blocked.status_code == 429


def test_ip_rate_limit_blocks_frequent_requests(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138206")
    headers = {"Authorization": f"Bearer {user['token']}", "x-forwarded-for": "10.0.0.6"}

    client.post("/api/pay/orders", headers=headers, json={"package_id": "pkg_300", "channel": "wechat"})
    client.post("/api/pay/callback/wechat", json={"order_id": 1, "status": "success"})

    statuses = []
    for index in range(6):
        response = client.post(
            "/api/generate/tasks",
            headers=headers,
            json={
                "prompt": f"IP 限流测试 {index}",
                "ratio_id": "ratio_square_1_1",
                "style_id": "style_han_dynasty",
                "template_id": "tpl_oc_avatar",
                "quality_level": "standard",
                "reference_image_urls": [],
            },
        )
        statuses.append(response.status_code)

    assert statuses[:4] == [200, 200, 200, 200]
    assert statuses[4:] == [429, 429]


def test_fallback_provider_is_used_when_primary_is_unavailable(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138207")
    headers = {"Authorization": f"Bearer {user['token']}", "x-forwarded-for": "10.0.0.7"}
    admin_code = client.post("/api/admin/login", json={"account": "admin", "password": "admin123"}).json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_code}"}

    client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
          "provider_id": "fallback-primary",
          "provider_name": "Fallback Primary",
          "base_url": "https://api.primary.com/v1",
          "api_key_ref": "env:PRIMARY",
          "model_name": "primary",
          "api_mode": "openai_compatible",
          "capabilities": ["text_to_image"],
          "priority": 1,
          "status": "unavailable",
          "timeout_seconds": 60,
          "qps_limit": 5,
          "cost_level": "medium"
        },
    )
    fallback = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
          "provider_id": "fallback-secondary",
          "provider_name": "Fallback Secondary",
          "base_url": "https://api.secondary.com/v1",
          "api_key_ref": "env:SECONDARY",
          "model_name": "secondary",
          "api_mode": "openai_compatible",
          "capabilities": ["text_to_image"],
          "priority": 2,
          "status": "healthy",
          "timeout_seconds": 60,
          "qps_limit": 5,
          "cost_level": "medium"
        },
    )

    response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "主模型不可用时走备用模型",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert response.status_code == 200
    assert fallback.status_code == 200

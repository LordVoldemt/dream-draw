from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'dream-draw-api-endpoints.db'}",
            }
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str = "13800138999") -> dict:
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


def test_auth_endpoints_reject_invalid_input_and_code(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    invalid_phone = client.post("/api/auth/sms/send-code", json={"phone": "1380013800a"})
    invalid_code = client.post("/api/auth/login", json={"phone": "13800138000", "code": "0000"})

    assert invalid_phone.status_code == 422
    assert invalid_phone.json()["error"]["code"] == "invalid_phone"
    assert invalid_code.status_code == 422
    assert invalid_code.json()["error"]["code"] == "invalid_code"


def test_generation_catalog_and_inspirations_endpoints_cover_filters_and_missing_group(
    tmp_path: Path,
) -> None:
    client = create_test_client(tmp_path)

    all_templates = client.get("/api/templates")
    xianxia_templates = client.get("/api/templates?style_id=style_xianxia")
    inspiration_group = client.get("/api/prompts/inspirations?group=recommended")
    missing_group = client.get("/api/prompts/inspirations?group=missing")

    assert all_templates.status_code == 200
    assert len(all_templates.json()["templates"]) == 8
    assert xianxia_templates.status_code == 200
    assert {item["id"] for item in xianxia_templates.json()["templates"]} == {
        "tpl_dreamgirl_portrait",
        "tpl_wallpaper_character",
        "tpl_character_sheet",
    }
    assert inspiration_group.status_code == 200
    assert inspiration_group.json()["group"] == "recommended"
    assert len(inspiration_group.json()["prompts"]) >= 1
    assert missing_group.status_code == 404
    assert missing_group.json()["error"]["code"] == "group_not_found"


def test_generation_quote_and_task_detail_errors_are_reported(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138901")
    owner_headers = {
        "Authorization": f"Bearer {user['token']}",
        "x-forwarded-for": "10.9.0.1",
    }

    quote_response = client.post(
        "/api/generate/quote",
        json={
            "ratio_id": "ratio_vertical_9_16",
            "style_id": "style_cinematic",
            "template_id": "tpl_video_cover",
            "quality_level": "ultra",
            "reference_image_count": 3,
        },
    )
    not_found_task = client.get("/api/generate/tasks/999", headers=owner_headers)

    assert quote_response.status_code == 200
    assert quote_response.json()["final_points"] >= 3
    assert not_found_task.status_code == 404
    assert not_found_task.json()["error"]["code"] == "task_not_found"


def test_generation_task_rejects_blocked_prompt_and_insufficient_points(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138902")
    headers = {
        "Authorization": f"Bearer {user['token']}",
        "x-forwarded-for": "10.9.0.2",
    }

    first_expensive_task = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "第一次高质量电影感角色海报",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_cinematic",
            "template_id": "tpl_video_cover",
            "quality_level": "ultra",
            "reference_image_urls": [
                "https://example.com/ref-1.png",
                "https://example.com/ref-2.png",
                "https://example.com/ref-3.png",
            ],
        },
    )

    blocked_prompt = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "这是一位未成年人角色设定图",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    insufficient_points = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "超高规格电影感角色海报",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_cinematic",
            "template_id": "tpl_video_cover",
            "quality_level": "ultra",
            "reference_image_urls": [
                "https://example.com/ref-1.png",
                "https://example.com/ref-2.png",
                "https://example.com/ref-3.png",
            ],
        },
    )

    assert first_expensive_task.status_code == 200
    assert blocked_prompt.status_code == 422
    assert blocked_prompt.json()["error"]["code"] == "blocked_prompt"
    assert insufficient_points.status_code == 409
    assert insufficient_points.json()["error"]["code"] == "insufficient_points"


def test_work_and_payment_endpoints_report_missing_or_invalid_resources(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138903")
    headers = {"Authorization": f"Bearer {user['token']}"}

    missing_work_detail = client.get("/api/works/999", headers=headers)
    missing_work_share = client.post("/api/works/999/share?channel=wechat", headers=headers)
    invalid_package = client.post(
        "/api/pay/orders",
        headers=headers,
        json={"package_id": "pkg_missing", "channel": "wechat"},
    )
    invalid_channel = client.post(
        "/api/pay/orders",
        headers=headers,
        json={"package_id": "pkg_30", "channel": "bank"},
    )
    missing_order = client.post(
        "/api/pay/callback/wechat",
        json={"order_id": 999, "status": "success"},
    )
    wrong_callback_channel = client.post(
        "/api/pay/callback/bank",
        json={"order_id": 1, "status": "success"},
    )

    assert missing_work_detail.status_code == 404
    assert missing_work_share.status_code == 404
    assert invalid_package.status_code == 422
    assert invalid_package.json()["error"]["code"] == "invalid_package"
    assert invalid_channel.status_code == 422
    assert invalid_channel.json()["error"]["code"] == "invalid_channel"
    assert missing_order.status_code == 404
    assert missing_order.json()["error"]["code"] == "order_not_found"
    assert wrong_callback_channel.status_code == 422
    assert wrong_callback_channel.json()["error"]["code"] == "invalid_channel"


def test_admin_endpoints_require_confirmation_and_validate_errors(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138904")
    admin_headers = {"Authorization": f"Bearer {login_admin(client)}"}
    user_id = user["user"]["id"]

    bad_admin_login = client.post("/api/admin/login", json={"account": "admin", "password": "wrong"})
    missing_confirm_points = client.patch(
        f"/api/admin/users/{user_id}/points",
        headers=admin_headers,
        json={"delta": 3, "reason": "", "confirm": False},
    )
    missing_confirm_status = client.patch(
        f"/api/admin/users/{user_id}/status",
        headers=admin_headers,
        json={"status": "frozen", "reason": "", "confirm": False},
    )
    missing_user_detail = client.get("/api/admin/users/999", headers=admin_headers)

    assert bad_admin_login.status_code == 401
    assert bad_admin_login.json()["error"]["code"] == "invalid_credentials"
    assert missing_confirm_points.status_code == 422
    assert missing_confirm_points.json()["error"]["code"] == "confirmation_required"
    assert missing_confirm_status.status_code == 422
    assert missing_confirm_status.json()["error"]["code"] == "confirmation_required"
    assert missing_user_detail.status_code == 404
    assert missing_user_detail.json()["error"]["code"] == "user_not_found"


def test_model_provider_endpoints_validate_api_mode_and_auth(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    admin_headers = {"Authorization": f"Bearer {login_admin(client)}"}

    unauthorized_list = client.get("/api/admin/model-providers")
    invalid_create = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "bad-provider",
            "provider_name": "Bad Provider",
            "base_url": "https://api.bad-provider.com/v1",
            "api_key_ref": "env:BAD_PROVIDER_KEY",
            "model_name": "bad-model",
            "api_mode": "custom_mode",
            "capabilities": ["text_to_image"],
            "priority": 9,
            "status": "healthy",
            "timeout_seconds": 30,
            "qps_limit": 2,
            "cost_level": "low",
        },
    )

    provider_create = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "good-provider",
            "provider_name": "Good Provider",
            "base_url": "https://api.good-provider.com/v1",
            "api_key_ref": "env:GOOD_PROVIDER_KEY",
            "model_name": "good-model",
            "api_mode": "openai_compatible",
            "capabilities": ["text_to_image"],
            "priority": 1,
            "status": "healthy",
            "timeout_seconds": 45,
            "qps_limit": 4,
            "cost_level": "medium",
        },
    )
    provider_id = provider_create.json()["provider"]["id"]
    invalid_update = client.patch(
        f"/api/admin/model-providers/{provider_id}",
        headers=admin_headers,
        json={
            "provider_id": "good-provider",
            "provider_name": "Good Provider",
            "base_url": "https://api.good-provider.com/v1",
            "api_key_ref": "env:GOOD_PROVIDER_KEY",
            "model_name": "good-model-v2",
            "api_mode": "custom_mode",
            "capabilities": ["text_to_image", "reference_image"],
            "priority": 2,
            "status": "degraded",
            "timeout_seconds": 50,
            "qps_limit": 5,
            "cost_level": "high",
        },
    )

    assert unauthorized_list.status_code == 401
    assert invalid_create.status_code == 422
    assert invalid_create.json()["error"]["code"] == "invalid_api_mode"
    assert provider_create.status_code == 200
    assert invalid_update.status_code == 422
    assert invalid_update.json()["error"]["code"] == "invalid_api_mode"

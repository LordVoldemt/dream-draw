from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'dream-draw-integration-test.db'}",
            }
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str) -> dict:
    code = client.post("/api/auth/sms/send-code", json={"phone": phone}).json()["mock_code"]
    return client.post("/api/auth/login", json={"phone": phone, "code": code}).json()


def login_admin(client: TestClient) -> str:
    response = client.post("/api/admin/login", json={"account": "admin", "password": "admin123"})
    return response.json()["token"]


def test_user_full_flow_home_login_generate_result_download(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    home_response = client.get("/health")
    assert home_response.status_code == 200

    login_payload = login_user(client, "13800138200")
    headers = {"Authorization": f"Bearer {login_payload['token']}", "x-forwarded-for": "10.0.0.1"}

    task_response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "盛唐时期华贵贵族女子，金色步摇，端庄华贵",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_tang_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert task_response.status_code == 200

    works_response = client.get("/api/works", headers=headers)
    work_id = works_response.json()["works"][0]["id"]
    result_response = client.get(f"/api/works/{work_id}", headers=headers)

    assert result_response.status_code == 200
    assert result_response.json()["work"]["image_url"].startswith("https://minio.local/")


def test_share_referral_flow_generates_link_and_new_user_can_complete_first_generation(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    owner = login_user(client, "13800138201")
    owner_headers = {"Authorization": f"Bearer {owner['token']}", "x-forwarded-for": "10.0.0.2"}

    client.post(
        "/api/generate/tasks",
        headers=owner_headers,
        json={
            "prompt": "白狐仙灵少女，银发狐耳，山雾与灵火",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_xianxia",
            "template_id": "tpl_wallpaper_character",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    works_response = client.get("/api/works", headers=owner_headers)
    work_id = works_response.json()["works"][0]["id"]
    share_response = client.post(f"/api/works/{work_id}/share?channel=wechat", headers=owner_headers)
    assert share_response.status_code == 200
    assert "share_code=" in share_response.json()["share_payload"]["share_link"]

    new_user = login_user(client, "13800138202")
    new_headers = {"Authorization": f"Bearer {new_user['token']}", "x-forwarded-for": "10.0.0.3"}
    first_task = client.post(
        "/api/generate/tasks",
        headers=new_headers,
        json={
            "prompt": "新中式冷艳女性，金属耳饰，封面感构图",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_new_chinese",
            "template_id": "tpl_xiaohongshu_cover",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert first_task.status_code == 200


def test_admin_full_flow_login_users_detail_providers_monitoring(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138203")
    user_id = user["user"]["id"]
    admin_headers = {"Authorization": f"Bearer {login_admin(client)}"}

    users_response = client.get("/api/admin/users", headers=admin_headers)
    detail_response = client.get(f"/api/admin/users/{user_id}", headers=admin_headers)
    provider_response = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "provider-flow",
            "provider_name": "Provider Flow",
            "base_url": "https://api.provider-flow.com/v1",
            "api_key_ref": "env:PROVIDER_FLOW_KEY",
            "model_name": "gufeng-flow",
            "api_mode": "openai_compatible",
            "capabilities": ["text_to_image"],
            "priority": 3,
            "status": "healthy",
            "timeout_seconds": 60,
            "qps_limit": 6,
            "cost_level": "medium",
        },
    )
    monitoring_response = client.get("/api/admin/model-monitoring", headers=admin_headers)

    assert users_response.status_code == 200
    assert detail_response.status_code == 200
    assert provider_response.status_code == 200
    assert monitoring_response.status_code == 200

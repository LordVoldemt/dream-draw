from pathlib import Path
from time import monotonic, sleep

from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'dream-draw-admin-test.db'}",
            }
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str = "13800138100") -> dict:
    code = client.post("/api/auth/sms/send-code", json={"phone": phone}).json()["mock_code"]
    return client.post("/api/auth/login", json={"phone": phone, "code": code}).json()


def login_admin(client: TestClient) -> str:
    response = client.post("/api/admin/login", json={"account": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["token"]


def wait_for_task_status(client: TestClient, task_id: int, token: str, expected_status: str) -> dict:
    deadline = monotonic() + 2
    headers = {"Authorization": f"Bearer {token}"}
    while monotonic() < deadline:
        response = client.get(f"/api/generate/tasks/{task_id}", headers=headers)
        assert response.status_code == 200
        task = response.json()["task"]
        if task["status"] == expected_status:
            return task
        sleep(0.02)
    raise AssertionError(f"task {task_id} did not reach {expected_status}")


def create_work(client: TestClient, user_token: str, prompt: str = "汉代温婉女子") -> int:
    response = client.post(
        "/api/generate/tasks",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "prompt": prompt,
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    task_detail = client.get(
        f"/api/generate/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    ).json()["task"]
    return int(task_detail["id"])


def test_works_list_detail_and_share_are_user_isolated(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    first_user = login_user(client, "13800138101")
    second_user = login_user(client, "13800138102")
    first_headers = {"Authorization": f"Bearer {first_user['token']}"}
    second_headers = {"Authorization": f"Bearer {second_user['token']}"}

    client.post(
        "/api/generate/tasks",
        headers=first_headers,
        json={
            "prompt": "小说女主设定图",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )

    works_response = client.get("/api/works", headers=first_headers)
    assert works_response.status_code == 200
    works = works_response.json()["works"]
    assert len(works) == 1
    work_id = works[0]["id"]

    detail_response = client.get(f"/api/works/{work_id}", headers=first_headers)
    share_response = client.post(f"/api/works/{work_id}/share?channel=wechat", headers=first_headers)
    forbidden_response = client.get(f"/api/works/{work_id}", headers=second_headers)

    assert detail_response.status_code == 200
    assert share_response.status_code == 200
    assert "share_link" in share_response.json()["share_payload"]
    assert forbidden_response.status_code == 403


def test_payment_order_and_callback_credit_points_once(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138103")
    headers = {"Authorization": f"Bearer {user['token']}"}

    order_response = client.post(
        "/api/pay/orders",
        headers=headers,
        json={"package_id": "pkg_30", "channel": "wechat"},
    )
    assert order_response.status_code == 200
    order_id = order_response.json()["order"]["id"]

    callback_response = client.post(
        "/api/pay/callback/wechat",
        json={"order_id": order_id, "status": "success"},
    )
    duplicate_response = client.post(
        "/api/pay/callback/wechat",
        json={"order_id": order_id, "status": "success"},
    )
    points_response = client.get("/api/points", headers=headers)

    assert callback_response.status_code == 200
    assert duplicate_response.json()["duplicate"] is True
    assert points_response.json()["balance"] == 40


def test_admin_can_manage_users_and_providers_and_monitoring(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138104")
    user_id = user["user"]["id"]
    admin_token = login_admin(client)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    users_response = client.get("/api/admin/users", headers=admin_headers)
    assert users_response.status_code == 200
    assert users_response.json()["users"][0]["masked_phone"].startswith("138****")

    detail_response = client.get(f"/api/admin/users/{user_id}", headers=admin_headers)
    assert detail_response.status_code == 200

    adjust_response = client.patch(
        f"/api/admin/users/{user_id}/points",
        headers=admin_headers,
        json={"delta": 5, "reason": "运营补偿", "confirm": True},
    )
    status_response = client.patch(
        f"/api/admin/users/{user_id}/status",
        headers=admin_headers,
        json={"status": "frozen", "reason": "风控冻结", "confirm": True},
    )
    assert adjust_response.status_code == 200
    assert status_response.status_code == 200

    provider_create = client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "provider-a",
            "provider_name": "Provider A",
            "base_url": "https://api.provider-a.com/v1",
            "api_key_ref": "env:PROVIDER_A_KEY",
            "model_name": "gufeng-v1",
            "api_mode": "openai_compatible",
            "capabilities": ["text_to_image"],
            "priority": 1,
            "status": "healthy",
            "timeout_seconds": 60,
            "qps_limit": 8,
            "cost_level": "medium",
        },
    )
    assert provider_create.status_code == 200
    provider_db_id = provider_create.json()["provider"]["id"]

    provider_update = client.patch(
        f"/api/admin/model-providers/{provider_db_id}",
        headers=admin_headers,
        json={
            "provider_id": "provider-a",
            "provider_name": "Provider A2",
            "base_url": "https://api.provider-a.com/v1",
            "api_key_ref": "env:PROVIDER_A_KEY",
            "model_name": "gufeng-v2",
            "api_mode": "openai_compatible",
            "capabilities": ["text_to_image", "reference_image"],
            "priority": 2,
            "status": "degraded",
            "timeout_seconds": 45,
            "qps_limit": 10,
            "cost_level": "high",
        },
    )
    provider_status = client.patch(
        f"/api/admin/model-providers/{provider_db_id}/status",
        headers=admin_headers,
        json={"status": "maintenance"},
    )
    provider_list = client.get("/api/admin/model-providers", headers=admin_headers)
    monitoring_response = client.get("/api/admin/model-monitoring", headers=admin_headers)
    overview_response = client.get("/api/admin/overview", headers=admin_headers)

    assert provider_update.status_code == 200
    assert provider_status.status_code == 200
    assert provider_list.status_code == 200
    assert monitoring_response.status_code == 200
    assert overview_response.status_code == 200
    assert "users_total" in overview_response.json()["overview"]


def test_worker_refunds_failed_or_blocked_tasks(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138105")
    headers = {"Authorization": f"Bearer {user['token']}"}
    admin_token = login_admin(client)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(
        "/api/admin/model-providers",
        headers=admin_headers,
        json={
            "provider_id": "provider-b",
            "provider_name": "Provider B",
            "base_url": "https://api.provider-b.com/v1",
            "api_key_ref": "env:PROVIDER_B_KEY",
            "model_name": "gufeng-v1",
            "api_mode": "openai_compatible",
            "capabilities": ["text_to_image"],
            "priority": 1,
            "status": "healthy",
            "timeout_seconds": 60,
            "qps_limit": 8,
            "cost_level": "medium",
        },
    )

    blocked_task = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "这张图会审核失败",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    failed_task = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "这张图会模型失败",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    points_response = client.get("/api/points", headers=headers)

    assert blocked_task.status_code == 200
    wait_for_task_status(client, blocked_task.json()["task_id"], user["token"], "blocked")
    assert failed_task.status_code == 200
    wait_for_task_status(client, failed_task.json()["task_id"], user["token"], "failed")
    assert points_response.json()["balance"] == 10


def test_favorite_lifecycle_and_share_channel_validation(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    user = login_user(client, "13800138106")
    other_user = login_user(client, "13800138107")
    headers = {"Authorization": f"Bearer {user['token']}"}
    other_headers = {"Authorization": f"Bearer {other_user['token']}"}

    client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "收藏测试作品",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_mode": "character",
            "reference_image_urls": [],
        },
    )

    works_response = client.get("/api/works", headers=headers)
    assert works_response.status_code == 200
    work_id = works_response.json()["works"][0]["id"]

    favorite_response = client.post(f"/api/works/{work_id}/favorite", headers=headers)
    detail_response = client.get(f"/api/works/{work_id}", headers=headers)
    forbidden_favorite_response = client.post(f"/api/works/{work_id}/favorite", headers=other_headers)
    invalid_share_response = client.post(f"/api/works/{work_id}/share?channel=facebook", headers=headers)
    unfavorite_response = client.request("DELETE", f"/api/works/{work_id}/favorite", headers=headers)

    assert favorite_response.status_code == 200
    assert detail_response.status_code == 200
    assert detail_response.json()["work"]["is_favorite"] is True
    assert forbidden_favorite_response.status_code == 403
    assert invalid_share_response.status_code == 422
    assert unfavorite_response.status_code == 200

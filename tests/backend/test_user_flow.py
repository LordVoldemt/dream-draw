from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import AppSettings
from app.main import create_app


def create_test_client(tmp_path: Path) -> TestClient:
    settings = AppSettings.from_env(
        {
            "database": {
                "url": f"sqlite:///{tmp_path / 'dream-draw-test.db'}",
            },
            "uploads_dir": str(tmp_path / "uploads"),
        }
    )
    return TestClient(create_app(settings))


def login_user(client: TestClient, phone: str = "13800138000") -> dict:
    send_response = client.post("/api/auth/sms/send-code", json={"phone": phone})
    assert send_response.status_code == 200
    code = send_response.json()["mock_code"]

    login_response = client.post(
        "/api/auth/login",
        json={"phone": phone, "code": code},
    )
    assert login_response.status_code == 200
    return login_response.json()


def test_first_login_creates_user_and_grants_bonus(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    payload = login_user(client)

    assert payload["is_first_login"] is True
    assert payload["user"]["points_balance"] == 10


def test_repeat_login_does_not_grant_bonus_twice(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    first_payload = login_user(client)
    second_payload = login_user(client)

    assert first_payload["user"]["id"] == second_payload["user"]["id"]
    assert second_payload["is_first_login"] is False
    assert second_payload["user"]["points_balance"] == 10


def test_profile_and_points_require_authentication(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    profile_response = client.get("/api/user/profile")
    points_response = client.get("/api/points")

    assert profile_response.status_code == 401
    assert points_response.status_code == 401


def test_profile_and_points_are_scoped_to_current_user(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    login_payload = login_user(client, "13800138001")
    headers = {"Authorization": f"Bearer {login_payload['token']}"}

    profile_response = client.get("/api/user/profile", headers=headers)
    points_response = client.get("/api/points", headers=headers)

    assert profile_response.status_code == 200
    assert profile_response.json()["profile"]["phone"] == "13800138001"
    assert points_response.status_code == 200
    assert points_response.json()["balance"] == 10
    assert len(points_response.json()["transactions"]) == 1


def test_styles_templates_and_inspirations_follow_catalog(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    styles_response = client.get("/api/styles")
    templates_response = client.get("/api/templates?style_id=style_xianxia")
    inspiration_response = client.get("/api/prompts/inspirations")

    assert styles_response.status_code == 200
    assert len(styles_response.json()["styles"]) == 6
    assert templates_response.status_code == 200
    assert "groups" in templates_response.json()
    assert inspiration_response.status_code == 200
    assert "recommended" in inspiration_response.json()["groups"]


def test_quote_endpoint_returns_breakdown(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)

    response = client.post(
        "/api/generate/quote",
        json={
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_tang_dynasty",
            "template_id": "tpl_dreamgirl_portrait",
            "quality_level": "hd",
            "reference_image_count": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["base_points"] == 2
    assert body["style_extra_points"] == 1
    assert body["template_extra_points"] == 1
    assert body["reference_image_extra_points"] == 2
    assert body["final_points"] == 6


def test_create_task_returns_immediately_and_persists_generated_assets(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    login_payload = login_user(client, "13800138002")
    headers = {"Authorization": f"Bearer {login_payload['token']}", "x-forwarded-for": "10.1.0.2"}

    response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "盛唐时期丰腴贵族女子，金色步摇，红色齐胸襦裙，端庄华贵",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )

    assert response.status_code == 200
    task_payload = response.json()
    assert task_payload["status"] in {"pending", "generating", "reviewing", "success"}
    assert task_payload["final_points"] == 1
    assert task_payload["work_id"] is None

    task_id = task_payload["task_id"]
    detail_response = client.get(f"/api/generate/tasks/{task_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["task"]["status"] == "success"

    work_by_task_response = client.get(f"/api/works-by-task/{task_id}", headers=headers)
    assert work_by_task_response.status_code == 200
    work = work_by_task_response.json()["work"]
    assert work["image_url"] == f"/uploads/works/task-{task_id}.png"
    assert work["thumbnail_url"] == f"/uploads/works/task-{task_id}-thumb.png"
    assert work["share_image_url"] == f"/uploads/works/task-{task_id}-share.png"

    uploads_dir = tmp_path / "uploads" / "works"
    assert (uploads_dir / f"task-{task_id}.png").exists()
    assert (uploads_dir / f"task-{task_id}-thumb.png").exists()
    assert (uploads_dir / f"task-{task_id}-share.png").exists()


def test_create_task_rejects_insufficient_points_and_blocked_prompt(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    login_payload = login_user(client, "13800138003")
    headers = {"Authorization": f"Bearer {login_payload['token']}", "x-forwarded-for": "10.1.0.3"}

    blocked_response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "未成年人国风写真",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_tang_dynasty",
            "template_id": "tpl_dreamgirl_portrait",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    assert blocked_response.status_code == 422

    expensive_response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "电影质感国风海报",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_cinematic",
            "template_id": "tpl_character_sheet",
            "quality_level": "ultra",
            "reference_image_urls": [
                "https://example.com/ref1.png",
                "https://example.com/ref2.png",
                "https://example.com/ref3.png",
            ],
        },
    )
    assert expensive_response.status_code == 200

    insufficient_response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "电影质感国风海报二次生成",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_cinematic",
            "template_id": "tpl_character_sheet",
            "quality_level": "ultra",
            "reference_image_urls": [
                "https://example.com/ref1.png",
                "https://example.com/ref2.png",
                "https://example.com/ref3.png",
            ],
        },
    )
    assert insufficient_response.status_code == 409


def test_task_detail_is_isolated_between_users(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    first_user = login_user(client, "13800138004")
    second_user = login_user(client, "13800138005")
    first_headers = {"Authorization": f"Bearer {first_user['token']}", "x-forwarded-for": "10.1.0.4"}
    second_headers = {"Authorization": f"Bearer {second_user['token']}", "x-forwarded-for": "10.1.0.5"}

    create_response = client.post(
        "/api/generate/tasks",
        headers=first_headers,
        json={
            "prompt": "汉代温婉女子",
            "ratio_id": "ratio_square_1_1",
            "style_id": "style_han_dynasty",
            "template_id": "tpl_oc_avatar",
            "quality_level": "standard",
            "reference_image_urls": [],
        },
    )
    task_id = create_response.json()["task_id"]

    forbidden_response = client.get(f"/api/generate/tasks/{task_id}", headers=second_headers)
    assert forbidden_response.status_code == 403


def test_create_task_persists_reference_mode(tmp_path: Path) -> None:
    client = create_test_client(tmp_path)
    login_payload = login_user(client, "13800138006")
    headers = {"Authorization": f"Bearer {login_payload['token']}", "x-forwarded-for": "10.1.0.6"}

    response = client.post(
        "/api/generate/tasks",
        headers=headers,
        json={
            "prompt": "新中式冷艳女性角色",
            "ratio_id": "ratio_portrait_3_4",
            "style_id": "style_new_chinese",
            "template_id": "tpl_dreamgirl_portrait",
            "quality_level": "standard",
            "reference_mode": "style",
            "reference_image_urls": ["https://example.com/ref-style.png"],
        },
    )

    assert response.status_code == 200
    detail_response = client.get(f"/api/generate/tasks/{response.json()['task_id']}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["task"]["reference_mode"] == "style"

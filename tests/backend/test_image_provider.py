from __future__ import annotations

import base64
import logging

import httpx

from app.core.errors import AppError
from app.infrastructure.database import Database
from app.infrastructure.repositories import (
    GenerationTaskRepository,
    ModelHealthLogRepository,
    ModelProviderRepository,
    PointTransactionRepository,
    UserRepository,
    WorkRepository,
)
from app.services import generation_worker
from app.services.image_provider import generate_image_assets


def test_generate_image_assets_calls_openai_compatible_provider_and_persists_local_files(tmp_path, monkeypatch) -> None:
    uploads_dir = tmp_path / "uploads"
    calls = []

    def fake_post(url: str, **kwargs):
        calls.append({"url": url, **kwargs})
        return httpx.Response(
            200,
            json={"data": [{"url": "https://cdn.example.com/generated.png"}]},
            request=httpx.Request("POST", url),
        )

    def fake_get(url: str, **kwargs):
        calls.append({"download_url": url, **kwargs})
        return httpx.Response(
            200,
            content=b"png-binary",
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    image_assets = generate_image_assets(
        "masterpiece, best quality, test prompt",
        {
            "base_url": "https://codeapi.swpumc.cn",
            "api_key_ref": "sk-test",
            "model_name": "gpt-image-2",
            "timeout_seconds": 60,
        },
        task_id=123,
        uploads_dir=str(uploads_dir),
    )

    assert image_assets == {
        "image_url": "/uploads/works/task-123.png",
        "thumbnail_url": "/uploads/works/task-123-thumb.png",
        "share_image_url": "/uploads/works/task-123-share.png",
    }
    assert calls[0]["url"] == "https://codeapi.swpumc.cn/v1/images/generations"
    assert calls[0]["headers"]["Authorization"] == "Bearer sk-test"
    assert calls[0]["json"]["model"] == "gpt-image-2"
    assert calls[0]["json"]["prompt"] == "masterpiece, best quality, test prompt"
    assert calls[1]["download_url"] == "https://cdn.example.com/generated.png"
    assert (uploads_dir / "works" / "task-123.png").read_bytes() == b"png-binary"
    assert (uploads_dir / "works" / "task-123-thumb.png").read_bytes() == b"png-binary"
    assert (uploads_dir / "works" / "task-123-share.png").read_bytes() == b"png-binary"


def test_generate_image_assets_supports_b64_json_response(tmp_path, monkeypatch) -> None:
    uploads_dir = tmp_path / "uploads"
    encoded = base64.b64encode(b"png-binary-from-b64").decode("utf-8")

    def fake_post(url: str, **kwargs):
        return httpx.Response(
            200,
            json={"data": [{"b64_json": encoded}]},
            request=httpx.Request("POST", url),
        )

    def fail_get(*_args, **_kwargs):
        raise AssertionError("should not download image when b64_json is present")

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fail_get)

    image_assets = generate_image_assets(
        "masterpiece, best quality, test prompt",
        {
            "base_url": "https://codeapi.swpumc.cn",
            "api_key_ref": "sk-test",
            "model_name": "gpt-image-2",
            "timeout_seconds": 60,
        },
        task_id=124,
        uploads_dir=str(uploads_dir),
    )

    assert image_assets == {
        "image_url": "/uploads/works/task-124.png",
        "thumbnail_url": "/uploads/works/task-124-thumb.png",
        "share_image_url": "/uploads/works/task-124-share.png",
    }
    assert (uploads_dir / "works" / "task-124.png").read_bytes() == b"png-binary-from-b64"
    assert (uploads_dir / "works" / "task-124-thumb.png").read_bytes() == b"png-binary-from-b64"
    assert (uploads_dir / "works" / "task-124-share.png").read_bytes() == b"png-binary-from-b64"


def test_generate_image_assets_logs_generation_payload(caplog, tmp_path, monkeypatch) -> None:
    uploads_dir = tmp_path / "uploads"

    def fake_post(url: str, **kwargs):
        return httpx.Response(
            200,
            json={"data": [{"b64_json": base64.b64encode(b"payload-log").decode("utf-8")}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    caplog.set_level(logging.WARNING)

    generate_image_assets(
        "A refined Chinese guofeng heroine portrait, elegant hanfu, soft studio lighting",
        {
            "base_url": "https://codeapi.swpumc.cn",
            "api_key_ref": "sk-test",
            "model_name": "gpt-image-2",
            "timeout_seconds": 60,
        },
        task_id=125,
        uploads_dir=str(uploads_dir),
    )

    assert "[image.provider.generate.request]" in caplog.text
    assert "gpt-image-2" in caplog.text
    assert "https://codeapi.swpumc.cn/v1/images/generations" in caplog.text
    assert "A refined Chinese guofeng heroine portrait" in caplog.text


def test_generate_image_assets_uses_local_mock_files_for_mock_provider(tmp_path) -> None:
    uploads_dir = tmp_path / "uploads"

    image_assets = generate_image_assets(
        "masterpiece, best quality, test prompt",
        {
            "base_url": "https://default-provider.local",
            "api_key_ref": "",
            "model_name": "mock-model",
            "timeout_seconds": 60,
        },
        task_id=456,
        uploads_dir=str(uploads_dir),
    )

    assert image_assets == {
        "image_url": "/uploads/works/task-456.png",
        "thumbnail_url": "/uploads/works/task-456-thumb.png",
        "share_image_url": "/uploads/works/task-456-share.png",
    }
    assert (uploads_dir / "works" / "task-456.png").exists()
    assert (uploads_dir / "works" / "task-456-thumb.png").exists()
    assert (uploads_dir / "works" / "task-456-share.png").exists()


def test_worker_refunds_points_when_provider_generation_fails(tmp_path, monkeypatch) -> None:
    database = Database(f"sqlite:///{tmp_path / 'provider-failure.db'}")
    database.initialize()
    users = UserRepository(database)
    tasks = GenerationTaskRepository(database)
    transactions = PointTransactionRepository(database)
    works = WorkRepository(database)
    providers = ModelProviderRepository(database)
    monitoring = ModelHealthLogRepository(database)

    user = users.create_user("13800138888", initial_points=10)
    task = tasks.create(
        user_id=int(user["id"]),
        prompt="test prompt",
        style_id="style_han_dynasty",
        template_id="tpl_oc_avatar",
        ratio_id="ratio_square_1_1",
        quality_level="standard",
        reference_mode=None,
        reference_image_count=0,
        final_points=1,
    )
    users.adjust_points(int(user["id"]), -1)

    def fail_generation(*_args, **_kwargs):
        raise AppError("image_provider_failed", "模型生成失败，请稍后重试", status_code=502)

    monkeypatch.setattr(generation_worker, "generate_image_assets", fail_generation)

    result = generation_worker.process_generation_task(
        task_id=int(task["id"]),
        tasks=tasks,
        users=users,
        transactions=transactions,
        works=works,
        providers=providers,
        monitoring=monitoring,
        uploads_dir=str(tmp_path / "uploads"),
    )

    assert result["status"] == "failed"
    assert users.find_by_id(int(user["id"]))["points_balance"] == 10
    assert works.list_by_user(int(user["id"])) == []

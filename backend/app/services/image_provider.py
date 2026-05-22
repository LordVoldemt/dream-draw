from __future__ import annotations

import base64
import logging
import shutil
from pathlib import Path
from typing import Any

import httpx

from app.core.errors import AppError

WORKS_SUBDIR = "works"
DEFAULT_GENERATION_TIMEOUT_SECONDS = 600
DEFAULT_DOWNLOAD_TIMEOUT_SECONDS = 600
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z0n8AAAAASUVORK5CYII=",
)
logger = logging.getLogger(__name__)


def should_use_mock_provider(provider: dict[str, Any]) -> bool:
    api_key_ref = str(provider.get("api_key_ref") or "")
    base_url = str(provider.get("base_url") or "")
    return not api_key_ref or api_key_ref.startswith("env:") or "default-provider.local" in base_url


def build_generation_payload(prompt: str, provider: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": provider["model_name"],
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }


def resolve_generation_timeout_seconds(provider: dict[str, Any]) -> float:
    timeout_seconds = float(provider.get("timeout_seconds") or DEFAULT_GENERATION_TIMEOUT_SECONDS)
    return max(timeout_seconds, float(DEFAULT_GENERATION_TIMEOUT_SECONDS))


def build_local_image_url(task_id: int) -> str:
    return f"/uploads/{WORKS_SUBDIR}/task-{task_id}.png"


def build_local_thumbnail_url(task_id: int) -> str:
    return f"/uploads/{WORKS_SUBDIR}/task-{task_id}-thumb.png"


def build_local_share_image_url(task_id: int) -> str:
    return f"/uploads/{WORKS_SUBDIR}/task-{task_id}-share.png"


def resolve_output_path(task_id: int, uploads_dir: str) -> Path:
    return Path(uploads_dir) / WORKS_SUBDIR / f"task-{task_id}.png"


def resolve_thumbnail_output_path(task_id: int, uploads_dir: str) -> Path:
    return Path(uploads_dir) / WORKS_SUBDIR / f"task-{task_id}-thumb.png"


def resolve_share_output_path(task_id: int, uploads_dir: str) -> Path:
    return Path(uploads_dir) / WORKS_SUBDIR / f"task-{task_id}-share.png"


def create_derivative_images(task_id: int, uploads_dir: str) -> None:
    source_path = resolve_output_path(task_id, uploads_dir)
    thumbnail_path = resolve_thumbnail_output_path(task_id, uploads_dir)
    share_path = resolve_share_output_path(task_id, uploads_dir)
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, thumbnail_path)
    shutil.copyfile(source_path, share_path)


def build_local_image_set(task_id: int, uploads_dir: str) -> dict[str, str]:
    create_derivative_images(task_id, uploads_dir)
    return {
        "image_url": build_local_image_url(task_id),
        "thumbnail_url": build_local_thumbnail_url(task_id),
        "share_image_url": build_local_share_image_url(task_id),
    }


def write_mock_image(task_id: int, uploads_dir: str) -> dict[str, str]:
    output_path = resolve_output_path(task_id, uploads_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(ONE_PIXEL_PNG)
    return build_local_image_set(task_id, uploads_dir)


def write_generated_image_bytes(image_bytes: bytes, task_id: int, uploads_dir: str) -> dict[str, str]:
    output_path = resolve_output_path(task_id, uploads_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return build_local_image_set(task_id, uploads_dir)


def download_image_to_local(image_url: str, task_id: int, uploads_dir: str) -> dict[str, str]:
    output_path = resolve_output_path(task_id, uploads_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = httpx.get(
            image_url,
            timeout=DEFAULT_DOWNLOAD_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AppError("image_download_failed", "生成图片下载失败，请稍后重试", status_code=502) from exc
    output_path.write_bytes(response.content)
    return build_local_image_set(task_id, uploads_dir)


def generate_image_assets(prompt: str, provider: dict[str, Any], task_id: int, uploads_dir: str) -> dict[str, str]:
    if should_use_mock_provider(provider):
        return write_mock_image(task_id, uploads_dir)

    base_url = str(provider["base_url"]).rstrip("/")
    endpoint = f"{base_url}/v1/images/generations"
    headers = {"Authorization": f"Bearer {provider['api_key_ref']}"}
    payload = build_generation_payload(prompt, provider)
    logger.warning(
        "[image.provider.generate.request] task_id=%s endpoint=%s payload=%s",
        task_id,
        endpoint,
        payload,
    )

    try:
        response = httpx.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=resolve_generation_timeout_seconds(provider),
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AppError("image_provider_failed", "模型生成失败，请稍后重试", status_code=502) from exc

    body = response.json()
    item = body.get("data", [{}])[0]
    image_b64 = item.get("b64_json")
    if image_b64:
        try:
            return write_generated_image_bytes(base64.b64decode(image_b64), task_id, uploads_dir)
        except ValueError as exc:
            raise AppError("image_provider_invalid_response", "模型返回的图片数据无效", status_code=502) from exc
    image_url = item.get("url")
    if image_url:
        return download_image_to_local(str(image_url), task_id, uploads_dir)
    raise AppError("image_provider_invalid_response", "模型未返回图片数据", status_code=502)

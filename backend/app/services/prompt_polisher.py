from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from app.core.errors import AppError

CHAT_PROVIDER_ID = "chat"
DEFAULT_POLISH_TIMEOUT_SECONDS = 60
MAX_POLISHED_PROMPT_LENGTH = 300
PROMPT_POLISH_SYSTEM_MESSAGE = (
    "你是绘梦平台的国风角色提示词润色助手。"
    "请把用户输入扩展为适合 AI 图像生成的中文提示词，保留原意，补充人物气质、服饰、材质、姿态、场景、光影和画面质感。"
    "不要加入真人明星、未成年人、政治人物、血腥暴力或露骨内容。"
    "只输出润色后的提示词，不要解释，不要编号，控制在 300 个汉字以内。"
)

logger = logging.getLogger(__name__)


def build_chat_completion_endpoint(provider: dict[str, Any]) -> str:
    base_url = str(provider["base_url"]).rstrip("/")
    if base_url.endswith("/v1"):
        return f"{base_url}/chat/completions"
    return f"{base_url}/v1/chat/completions"


def build_prompt_polish_payload(prompt: str, provider: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": provider["model_name"],
        "messages": [
            {"role": "system", "content": PROMPT_POLISH_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 260,
    }


def resolve_prompt_polish_timeout_seconds(provider: dict[str, Any]) -> float:
    timeout_seconds = float(provider.get("timeout_seconds") or DEFAULT_POLISH_TIMEOUT_SECONDS)
    return max(1.0, timeout_seconds)


def resolve_prompt_polish_api_key(provider: dict[str, Any]) -> str:
    api_key_ref = str(provider.get("api_key_ref") or "").strip()
    if api_key_ref.startswith("env:"):
        api_key = os.getenv(api_key_ref.removeprefix("env:").strip(), "")
    else:
        api_key = api_key_ref
    if not api_key:
        raise AppError("prompt_polish_provider_invalid", "润色模型密钥未配置", status_code=422)
    return api_key


def normalize_polished_prompt(content: str) -> str:
    polished_prompt = content.strip().strip("\"'“”‘’")
    if not polished_prompt:
        raise AppError("prompt_polish_invalid_response", "润色服务未返回有效内容", status_code=502)
    return polished_prompt[:MAX_POLISHED_PROMPT_LENGTH]


def extract_polished_prompt(body: dict[str, Any]) -> str:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AppError("prompt_polish_invalid_response", "润色服务返回格式异常", status_code=502)
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise AppError("prompt_polish_invalid_response", "润色服务返回格式异常", status_code=502)
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise AppError("prompt_polish_invalid_response", "润色服务返回格式异常", status_code=502)
    content = message.get("content")
    if not isinstance(content, str):
        raise AppError("prompt_polish_invalid_response", "润色服务返回格式异常", status_code=502)
    return normalize_polished_prompt(content)


def polish_prompt_with_provider(prompt: str, provider: dict[str, Any]) -> str:
    if provider.get("status") not in {"healthy", "degraded"}:
        raise AppError("prompt_polish_provider_unavailable", "润色模型暂不可用，请稍后再试", status_code=409)
    if provider.get("api_mode") != "openai_compatible":
        raise AppError("prompt_polish_provider_invalid", "润色模型配置不支持当前协议", status_code=422)

    endpoint = build_chat_completion_endpoint(provider)
    payload = build_prompt_polish_payload(prompt, provider)
    headers = {"Authorization": f"Bearer {resolve_prompt_polish_api_key(provider)}"}
    logger.warning(
        "[prompt.polish.request] provider_id=%s endpoint=%s prompt_length=%s",
        provider.get("provider_id"),
        endpoint,
        len(prompt),
    )

    try:
        response = httpx.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=resolve_prompt_polish_timeout_seconds(provider),
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AppError("prompt_polish_provider_failed", "润色服务暂不可用，请稍后再试", status_code=502) from exc

    return extract_polished_prompt(response.json())

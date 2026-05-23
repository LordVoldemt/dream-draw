from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx
import pytest


def _enabled() -> bool:
    return os.getenv("RUN_GPT_IMAGE2_OPENAI_COMPATIBLE_TESTS") == "1"


class TestGptImage2OpenAICompatibleGeneration:
    @pytest.mark.skipif(not _enabled(), reason="requires RUN_GPT_IMAGE2_OPENAI_COMPATIBLE_TESTS=1")
    def test_generate_image_with_openai_compatible_images_api(self, tmp_path: Path) -> None:
        base_url = os.environ["GPT_IMAGE2_OPENAI_COMPATIBLE_BASE_URL"].rstrip("/")
        api_key = os.environ["GPT_IMAGE2_OPENAI_COMPATIBLE_API_KEY"]
        model = os.environ.get("GPT_IMAGE2_OPENAI_COMPATIBLE_MODEL", "gpt-image-2")
        output_path = tmp_path / "gpt-image2-openai-compatible.png"

        response = httpx.post(
            f"{base_url}/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "prompt": "A refined Chinese guofeng heroine portrait, elegant hanfu, soft studio lighting",
                "n": 1,
                "size": "1024x1024",
            },
            timeout=600,
        )
        response.raise_for_status()

        item = response.json()["data"][0]
        if item.get("b64_json"):
            output_path.write_bytes(base64.b64decode(item["b64_json"]))
        else:
            image_response = httpx.get(item["url"], timeout=600, follow_redirects=True)
            image_response.raise_for_status()
            output_path.write_bytes(image_response.content)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

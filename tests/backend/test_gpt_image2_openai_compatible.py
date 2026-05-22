from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx
import pytest


def _enabled() -> bool:
    return os.getenv("RUN_GPT_IMAGE2_OPENAI_COMPATIBLE_TESTS") == "1"


class TestGptImage2OpenAICompatibleGeneration:
    def test_generate_image_with_openai_compatible_images_api(self, tmp_path: Path) -> None:
        base_url = "https://codeapi.swpumc.cn"
        api_key = "sk-b325468059d0e038738e6ba6330c4832b2bce5d6cacf6da6e595d21e7d742e99"
        model ="gpt-image-2"
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

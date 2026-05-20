from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


CATALOG_PATH = Path(__file__).resolve().parents[3] / "shared" / "product-catalog.json"


@lru_cache(maxsize=1)
def load_product_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)

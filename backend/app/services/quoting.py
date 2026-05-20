from __future__ import annotations

from dataclasses import dataclass

from app.core.errors import AppError
from app.shared.catalog import load_product_catalog


@dataclass
class QuoteBreakdown:
    base_points: int
    style_extra_points: int
    template_extra_points: int
    reference_image_extra_points: int
    ratio_extra_points: int
    final_points: int


def _find_entry(entries: list[dict], entry_id: str, label: str) -> dict:
    for entry in entries:
        if entry["id"] == entry_id:
            return entry
    raise AppError("invalid_enum", f"{label} 不存在", status_code=422)


def calculate_generation_quote(
    style_id: str,
    template_id: str,
    ratio_id: str,
    quality_level: str,
    reference_image_count: int,
) -> QuoteBreakdown:
    if reference_image_count not in {0, 1, 2, 3}:
        raise AppError("invalid_reference_count", "参考图数量仅支持 0 到 3 张", status_code=422)

    catalog = load_product_catalog()
    style = _find_entry(catalog["styles"], style_id, "风格")
    template = _find_entry(catalog["templates"], template_id, "模板")
    ratio = _find_entry(catalog["ratios"], ratio_id, "比例")
    quality = _find_entry(catalog["qualityLevels"], quality_level, "质量档位")
    reference_rule = next(
        rule for rule in catalog["referenceImagePoints"] if rule["count"] == reference_image_count
    )

    base_points = int(quality["basePoints"])
    style_extra = int(style["extraPoints"])
    template_extra = int(template["extraPoints"])
    ratio_extra = int(ratio["extraPoints"])
    reference_extra = int(reference_rule["extraPoints"])
    final_points = base_points + style_extra + template_extra + ratio_extra + reference_extra

    return QuoteBreakdown(
        base_points=base_points,
        style_extra_points=style_extra,
        template_extra_points=template_extra,
        reference_image_extra_points=reference_extra,
        ratio_extra_points=ratio_extra,
        final_points=final_points,
    )

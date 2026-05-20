from app.shared.catalog import load_product_catalog


def test_product_catalog_contains_required_enum_sets() -> None:
    catalog = load_product_catalog()

    assert [style["id"] for style in catalog["styles"]] == [
        "style_tang_dynasty",
        "style_han_dynasty",
        "style_xianxia",
        "style_new_chinese",
        "style_gufeng_portrait",
        "style_cinematic",
    ]
    assert [template["id"] for template in catalog["templates"]] == [
        "tpl_oc_avatar",
        "tpl_dreamgirl_portrait",
        "tpl_novel_heroine",
        "tpl_hanfu_photoshoot",
        "tpl_wallpaper_character",
        "tpl_xiaohongshu_cover",
        "tpl_video_cover",
        "tpl_character_sheet",
    ]
    assert [ratio["id"] for ratio in catalog["ratios"]] == [
        "ratio_square_1_1",
        "ratio_portrait_3_4",
        "ratio_portrait_2_3",
        "ratio_landscape_4_3",
        "ratio_landscape_16_9",
        "ratio_vertical_9_16",
    ]
    assert catalog["modelStatuses"] == [
        "healthy",
        "degraded",
        "unavailable",
        "maintenance",
    ]
    assert catalog["taskStatuses"] == [
        "pending",
        "generating",
        "reviewing",
        "success",
        "failed",
        "blocked",
    ]

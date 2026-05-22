import logging
import traceback
from threading import Thread

from pydantic import BaseModel, Field, HttpUrl
from fastapi import APIRouter, Depends, Query, Request

from app.core.config import AppSettings
from app.core.errors import AppError
from app.dependencies import (
    get_app_settings,
    get_current_user_id,
    get_generation_task_repository,
    get_model_health_log_repository,
    get_model_provider_repository,
    get_point_transaction_repository,
    get_user_repository,
    get_work_repository,
)
from app.infrastructure.repositories import (
    GenerationTaskRepository,
    ModelHealthLogRepository,
    ModelProviderRepository,
    PointTransactionRepository,
    UserRepository,
    WorkRepository,
)
from app.services.generation_worker import process_generation_task
from app.services.quoting import calculate_generation_quote
from app.services.rate_limit import ip_rate_limiter
from app.shared.catalog import load_product_catalog

router = APIRouter(tags=["generation"])
logger = logging.getLogger(__name__)


@router.get("/generate/_module")
async def module_info() -> dict[str, str]:
    return {"module": "generation"}


INSPIRATION_PROMPTS = {
    "recommended": [
        "盛唐时期华贵贵族女子",
        "仙侠白衣少女",
        "新中式冷艳女性",
    ],
    "recent_hot": [
        "长安贵族千金，金步摇与红色齐胸襦裙",
        "病娇红衣妖姬，月下回眸",
    ],
    "xiaohongshu_hot": [
        "新中式高级感头像，冷艳金属耳饰",
        "清冷月下女剑仙，白衣长剑与飞雪",
    ],
    "hanfu_hot": [
        "汉代温婉女子，曲裾深衣，古朴庭院",
        "汉服写真少女，园林回廊与柔光",
    ],
}


class QuoteRequest(BaseModel):
    ratio_id: str
    style_id: str
    template_id: str
    quality_level: str
    reference_image_url: HttpUrl | None = None
    reference_image_count: int = Field(ge=0, le=3)


class CreateTaskRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=300)
    ratio_id: str
    style_id: str
    template_id: str
    quality_level: str
    reference_mode: str | None = None
    reference_image_urls: list[HttpUrl] = Field(default_factory=list, max_length=3)


@router.get("/styles")
async def get_styles() -> dict:
    return {"styles": load_product_catalog()["styles"]}


@router.get("/templates")
async def get_templates(style_id: str | None = Query(default=None)) -> dict:
    catalog = load_product_catalog()
    templates = catalog["templates"]
    if style_id:
        if style_id == "style_han_dynasty":
            templates = [item for item in templates if item["id"] in {"tpl_hanfu_photoshoot", "tpl_novel_heroine", "tpl_character_sheet"}]
        elif style_id == "style_xianxia":
            templates = [item for item in templates if item["id"] in {"tpl_dreamgirl_portrait", "tpl_wallpaper_character", "tpl_character_sheet"}]

    return {
        "templates": templates,
        "groups": {
            "recent_hot": ["tpl_dreamgirl_portrait", "tpl_novel_heroine"],
            "xiaohongshu_hot": ["tpl_xiaohongshu_cover", "tpl_oc_avatar"],
            "hanfu_hot": ["tpl_hanfu_photoshoot", "tpl_character_sheet"],
        },
    }


@router.get("/prompts/inspirations")
async def get_inspirations(group: str | None = Query(default=None)) -> dict:
    if group:
        prompts = INSPIRATION_PROMPTS.get(group)
        if prompts is None:
            raise AppError("group_not_found", "灵感分组不存在", status_code=404)
        return {"group": group, "prompts": prompts}
    return {"groups": INSPIRATION_PROMPTS}


@router.post("/generate/quote")
async def quote_generation(payload: QuoteRequest) -> dict:
    breakdown = calculate_generation_quote(
        style_id=payload.style_id,
        template_id=payload.template_id,
        ratio_id=payload.ratio_id,
        quality_level=payload.quality_level,
        reference_image_count=payload.reference_image_count,
    )
    return {
        "base_points": breakdown.base_points,
        "style_extra_points": breakdown.style_extra_points,
        "template_extra_points": breakdown.template_extra_points,
        "reference_image_extra_points": breakdown.reference_image_extra_points,
        "ratio_extra_points": breakdown.ratio_extra_points,
        "final_points": breakdown.final_points,
    }


def _validate_prompt(prompt: str) -> None:
    blocked_keywords = ["未成年人", "真人明星", "政治人物", "血腥暴力"]
    for keyword in blocked_keywords:
        if keyword in prompt:
            raise AppError("blocked_prompt", "当前描述包含受限内容，请调整后重试", status_code=422)


def _run_generation_task_in_background(
    task_id: int,
    request_id: str,
    tasks: GenerationTaskRepository,
    users: UserRepository,
    transactions: PointTransactionRepository,
    works: WorkRepository,
    providers: ModelProviderRepository,
    monitoring: ModelHealthLogRepository,
    uploads_dir: str,
) -> None:
    try:
        process_generation_task(
            task_id=task_id,
            tasks=tasks,
            users=users,
            transactions=transactions,
            works=works,
            providers=providers,
            monitoring=monitoring,
            uploads_dir=uploads_dir,
        )
        logger.warning("[generate.tasks.background.done] request_id=%s task_id=%s", request_id, task_id)
    except Exception as exc:
        logger.error(
            "[generate.tasks.background.unhandled] request_id=%s task_id=%s error_type=%s error=%s traceback=%s",
            request_id,
            task_id,
            type(exc).__name__,
            str(exc),
            traceback.format_exc(),
        )


@router.post("/generate/tasks")
async def create_generation_task(
    request: Request,
    payload: CreateTaskRequest,
    user_id: int = Depends(get_current_user_id),
    users: UserRepository = Depends(get_user_repository),
    tasks: GenerationTaskRepository = Depends(get_generation_task_repository),
    transactions: PointTransactionRepository = Depends(get_point_transaction_repository),
    works: WorkRepository = Depends(get_work_repository),
    providers: ModelProviderRepository = Depends(get_model_provider_repository),
    monitoring: ModelHealthLogRepository = Depends(get_model_health_log_repository),
    settings: AppSettings = Depends(get_app_settings),
) -> dict:
    request_id = request.headers.get("x-request-id") or f"generate-{user_id}-{request.headers.get('x-forwarded-for', 'unknown')}"
    payload_summary = {
        "style_id": payload.style_id,
        "template_id": payload.template_id,
        "ratio_id": payload.ratio_id,
        "quality_level": payload.quality_level,
        "reference_count": len(payload.reference_image_urls),
        "prompt_length": len(payload.prompt),
    }
    logger.warning("[generate.tasks.start] request_id=%s user_id=%s payload=%s", request_id, user_id, payload_summary)
    try:
        _validate_prompt(payload.prompt)
        if len(payload.reference_image_urls) > 3:
            raise AppError("too_many_references", "最多支持 3 张参考图", status_code=422)
        ip_address = request.headers.get("x-forwarded-for", "unknown").split(",")[0].strip()
        logger.warning("[generate.tasks.ip] request_id=%s ip=%s", request_id, ip_address)
        if not ip_rate_limiter.allow(ip_address):
            raise AppError("ip_rate_limited", "当前 IP 请求过于频繁，请稍后再试", status_code=429)
        active_task_count = tasks.count_active_for_user(user_id)
        created_today_count = tasks.count_created_today_for_user(user_id)
        logger.warning(
            "[generate.tasks.limits] request_id=%s user_id=%s active_task_count=%s created_today_count=%s",
            request_id,
            user_id,
            active_task_count,
            created_today_count,
        )
        if active_task_count >= 3:
            raise AppError("rate_limited", "当前生成任务过多，请稍后再试", status_code=429)
        if created_today_count >= 20:
            raise AppError("daily_limit_reached", "新用户当日生成次数已达上限", status_code=429)
        if tasks.has_duplicate_prompt_today(user_id, payload.prompt):
            raise AppError("duplicate_prompt", "相同 Prompt 今日已提交，请调整描述后再试", status_code=409)

        quote = calculate_generation_quote(
            style_id=payload.style_id,
            template_id=payload.template_id,
            ratio_id=payload.ratio_id,
            quality_level=payload.quality_level,
            reference_image_count=len(payload.reference_image_urls),
        )
        logger.warning("[generate.tasks.quote] request_id=%s final_points=%s", request_id, quote.final_points)
        user = users.find_by_id(user_id)
        assert user is not None
        logger.warning("[generate.tasks.user] request_id=%s user_id=%s points_balance=%s", request_id, user_id, user["points_balance"])
        if int(user["points_balance"]) < quote.final_points:
            raise AppError("insufficient_points", "积分不足，请先充值", status_code=409)

        users.adjust_points(user_id, -quote.final_points)
        task = tasks.create(
            user_id=user_id,
            prompt=payload.prompt,
            style_id=payload.style_id,
            template_id=payload.template_id,
            ratio_id=payload.ratio_id,
            quality_level=payload.quality_level,
            reference_mode=payload.reference_mode,
            reference_image_count=len(payload.reference_image_urls),
            final_points=quote.final_points,
        )
        logger.warning("[generate.tasks.created] request_id=%s task_id=%s", request_id, task["id"])
        transactions.create(
            user_id=user_id,
            delta=-quote.final_points,
            transaction_type="generation_consume",
            reason="创建生成任务扣除积分",
            related_task_id=int(task["id"]),
        )
        logger.warning("[generate.tasks.transaction] request_id=%s task_id=%s points=%s", request_id, task["id"], quote.final_points)
        thread = Thread(
            target=_run_generation_task_in_background,
            args=(
                int(task["id"]),
                request_id,
                tasks,
                users,
                transactions,
                works,
                providers,
                monitoring,
                settings.uploads_dir,
            ),
            daemon=True,
        )
        thread.start()
        current_task = tasks.find_by_id(int(task["id"])) or task
        response = {
            "task_id": current_task["id"],
            "status": current_task["status"],
            "final_points": current_task["final_points"],
            "work_id": None,
        }
        logger.warning("[generate.tasks.accepted] request_id=%s response=%s", request_id, response)
        return response
    except AppError as exc:
        logger.exception(
            "[generate.tasks.app_error] request_id=%s user_id=%s code=%s status_code=%s message=%s payload=%s",
            request_id,
            user_id,
            exc.code,
            exc.status_code,
            exc.message,
            payload_summary,
        )
        raise
    except Exception as exc:
        logger.error(
            "[generate.tasks.unhandled] request_id=%s user_id=%s error_type=%s error=%s payload=%s traceback=%s",
            request_id,
            user_id,
            type(exc).__name__,
            str(exc),
            payload_summary,
            traceback.format_exc(),
        )
        raise


@router.get("/generate/tasks/{task_id}")
async def get_generation_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    tasks: GenerationTaskRepository = Depends(get_generation_task_repository),
) -> dict:
    task = tasks.find_by_id(task_id)
    if task is None:
        raise AppError("task_not_found", "生成任务不存在", status_code=404)
    if int(task["user_id"]) != user_id:
        raise AppError("forbidden", "无权查看该任务", status_code=403)
    return {"task": task}

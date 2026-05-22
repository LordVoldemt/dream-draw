from __future__ import annotations

import logging
import traceback
from typing import Any

from app.core.errors import AppError
from app.infrastructure.repositories import (
    GenerationTaskRepository,
    ModelProviderRepository,
    ModelHealthLogRepository,
    PointTransactionRepository,
    UserRepository,
    WorkRepository,
)
from app.services.image_provider import generate_image_assets

logger = logging.getLogger(__name__)


def enhance_prompt(task: dict[str, Any], style_keywords: list[str]) -> str:
    suffix = ", ".join(style_keywords)
    return f"masterpiece, best quality, {task['prompt']}, {suffix}, ultra detailed"


def process_generation_task(
    task_id: int,
    tasks: GenerationTaskRepository,
    users: UserRepository,
    transactions: PointTransactionRepository,
    works: WorkRepository,
    providers: ModelProviderRepository,
    monitoring: ModelHealthLogRepository,
    uploads_dir: str,
) -> dict[str, Any]:
    logger.warning("[generation.worker.start] task_id=%s uploads_dir=%s", task_id, uploads_dir)
    task = tasks.find_by_id(task_id)
    if task is None:
        logger.error("[generation.worker.task_missing] task_id=%s", task_id)
        raise ValueError("task not found")

    provider = providers.select_provider_for_generation()
    logger.warning(
        "[generation.worker.provider.selected] task_id=%s provider_id=%s provider_name=%s provider_model=%s",
        task_id,
        None if provider is None else provider.get("provider_id"),
        None if provider is None else provider.get("display_name"),
        None if provider is None else provider.get("model_name"),
    )
    if provider is None:
        tasks.update_status(task_id, "failed")
        users.adjust_points(int(task["user_id"]), int(task["final_points"]))
        transactions.create(
            user_id=int(task["user_id"]),
            delta=int(task["final_points"]),
            transaction_type="generation_refund",
            reason="模型不可用，自动退回积分",
            related_task_id=task_id,
        )
        logger.warning("[generation.worker.no_provider] task_id=%s refunded_points=%s", task_id, task["final_points"])
        return tasks.find_by_id(task_id) or task

    tasks.update_status(task_id, "generating", provider_id=provider["provider_id"])
    task = tasks.find_by_id(task_id) or task
    logger.warning("[generation.worker.status] task_id=%s status=%s", task_id, task["status"])

    if "审核失败" in task["prompt"] or "违禁" in task["prompt"]:
        tasks.update_status(task_id, "blocked")
        users.adjust_points(int(task["user_id"]), int(task["final_points"]))
        transactions.create(
            user_id=int(task["user_id"]),
            delta=int(task["final_points"]),
            transaction_type="generation_refund",
            reason="审核未通过，自动退回积分",
            related_task_id=task_id,
        )
        monitoring.record(
            provider_internal_id=int(provider["id"]),
            status="healthy",
            success_rate=0.0,
            average_latency_ms=800,
            timeout_count=0,
            failure_count=0,
            blocked_rate=1.0,
            queue_depth=0,
        )
        logger.warning("[generation.worker.blocked] task_id=%s", task_id)
        return tasks.find_by_id(task_id) or task

    if "模型失败" in task["prompt"]:
        tasks.update_status(task_id, "failed")
        users.adjust_points(int(task["user_id"]), int(task["final_points"]))
        transactions.create(
            user_id=int(task["user_id"]),
            delta=int(task["final_points"]),
            transaction_type="generation_refund",
            reason="生成失败，自动退回积分",
            related_task_id=task_id,
        )
        monitoring.record(
            provider_internal_id=int(provider["id"]),
            status="degraded",
            success_rate=0.0,
            average_latency_ms=1600,
            timeout_count=1,
            failure_count=1,
            blocked_rate=0.0,
            queue_depth=0,
        )
        logger.warning("[generation.worker.mock_failure] task_id=%s", task_id)
        return tasks.find_by_id(task_id) or task

    tasks.update_status(task_id, "reviewing")
    task = tasks.find_by_id(task_id) or task
    logger.warning("[generation.worker.status] task_id=%s status=%s", task_id, task["status"])
    try:
        prompt = enhance_prompt(task, ["cinematic"])
        logger.warning("[generation.worker.generate.begin] task_id=%s prompt_length=%s", task_id, len(prompt))
        image_assets = generate_image_assets(prompt, provider, task_id, uploads_dir)
        logger.warning("[generation.worker.generate.done] task_id=%s image_assets=%s", task_id, image_assets)
    except AppError as exc:
        logger.exception(
            "[generation.worker.app_error] task_id=%s code=%s status_code=%s message=%s",
            task_id,
            exc.code,
            exc.status_code,
            exc.message,
        )
        tasks.update_status(task_id, "failed")
        users.adjust_points(int(task["user_id"]), int(task["final_points"]))
        transactions.create(
            user_id=int(task["user_id"]),
            delta=int(task["final_points"]),
            transaction_type="generation_refund",
            reason="模型生成失败，自动退回积分",
            related_task_id=task_id,
        )
        monitoring.record(
            provider_internal_id=int(provider["id"]),
            status="degraded",
            success_rate=0.0,
            average_latency_ms=0,
            timeout_count=1,
            failure_count=1,
            blocked_rate=0.0,
            queue_depth=max(tasks.count_global_active() - 1, 0),
        )
        logger.warning("[generation.worker.failed_and_refunded] task_id=%s", task_id)
        return tasks.find_by_id(task_id) or task
    except Exception as exc:
        logger.error(
            "[generation.worker.unhandled] task_id=%s error_type=%s error=%s traceback=%s",
            task_id,
            type(exc).__name__,
            str(exc),
            traceback.format_exc(),
        )
        raise
    work = works.create(
        user_id=int(task["user_id"]),
        task_id=task_id,
        image_url=image_assets["image_url"],
        thumbnail_url=image_assets["thumbnail_url"],
        share_image_url=image_assets["share_image_url"],
        review_status="approved",
        prompt_snapshot=enhance_prompt(task, ["cinematic"]),
        style_id=task["style_id"],
        template_id=task["template_id"],
        ratio_id=task["ratio_id"],
        quality_level=task["quality_level"],
        reference_mode=task.get("reference_mode"),
        reference_image_count=int(task["reference_image_count"]),
        final_points=int(task["final_points"]),
    )
    logger.warning("[generation.worker.work.created] task_id=%s work_id=%s", task_id, work["id"])
    tasks.update_status(task_id, "success")
    monitoring.record(
        provider_internal_id=int(provider["id"]),
        status="healthy",
        success_rate=1.0,
        average_latency_ms=1200,
        timeout_count=0,
        failure_count=0,
        blocked_rate=0.0,
        queue_depth=max(tasks.count_global_active() - 1, 0),
    )
    logger.warning("[generation.worker.success] task_id=%s", task_id)
    return {"task": tasks.find_by_id(task_id), "work": work}

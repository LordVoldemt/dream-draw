from __future__ import annotations

from typing import Any

from app.infrastructure.repositories import (
    GenerationTaskRepository,
    ModelProviderRepository,
    ModelHealthLogRepository,
    PointTransactionRepository,
    UserRepository,
    WorkRepository,
)


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
) -> dict[str, Any]:
    task = tasks.find_by_id(task_id)
    if task is None:
        raise ValueError("task not found")

    provider = providers.select_provider_for_generation()
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
        return tasks.find_by_id(task_id) or task

    tasks.update_status(task_id, "generating", provider_id=provider["provider_id"])
    task = tasks.find_by_id(task_id) or task

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
        return tasks.find_by_id(task_id) or task

    tasks.update_status(task_id, "reviewing")
    task = tasks.find_by_id(task_id) or task
    image_url = f"https://minio.local/works/task-{task_id}.png"
    work = works.create(
        user_id=int(task["user_id"]),
        task_id=task_id,
        image_url=image_url,
        thumbnail_url=image_url.replace(".png", "-thumb.png"),
        share_image_url=image_url.replace(".png", "-share.png"),
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
    return {"task": tasks.find_by_id(task_id), "work": work}

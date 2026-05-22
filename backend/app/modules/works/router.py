import secrets

from fastapi import APIRouter, Depends, Query

from app.core.errors import AppError
from app.dependencies import (
    get_current_user_id,
    get_favorite_repository,
    get_share_event_repository,
    get_work_repository,
)
from app.infrastructure.repositories import FavoriteRepository, ShareEventRepository, WorkRepository

router = APIRouter(prefix="/works", tags=["works"])

ALLOWED_SHARE_CHANNELS = {"xiaohongshu", "wechat", "qq", "weibo"}


@router.get("/_module")
async def module_info() -> dict[str, str]:
    return {"module": "works"}


@router.get("")
async def list_works(
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
) -> dict:
    favorite_work_ids = set(favorites.list_work_ids_by_user(user_id))
    items = works.list_by_user(user_id)
    for item in items:
        item["is_favorite"] = int(item["id"]) in favorite_work_ids
    return {"works": items}


@router.get("/{work_id}")
async def get_work_detail(
    work_id: int,
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
) -> dict:
    work = works.find_by_id(work_id)
    if work is None:
        raise AppError("work_not_found", "作品不存在", status_code=404)
    if int(work["user_id"]) != user_id:
        raise AppError("forbidden", "无权查看该作品", status_code=403)
    work["is_favorite"] = favorites.exists(user_id, work_id)
    return {"work": work}


@router.get("-by-task/{task_id}")
async def get_work_detail_by_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
) -> dict:
    work = works.find_by_task_id(task_id)
    if work is None:
        raise AppError("work_not_found", "作品不存在", status_code=404)
    if int(work["user_id"]) != user_id:
        raise AppError("forbidden", "无权查看该作品", status_code=403)
    work["is_favorite"] = favorites.exists(user_id, int(work["id"]))
    return {"work": work}


@router.post("/{work_id}/favorite")
async def favorite_work(
    work_id: int,
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
) -> dict:
    work = works.find_by_id(work_id)
    if work is None:
        raise AppError("work_not_found", "作品不存在", status_code=404)
    if int(work["user_id"]) != user_id:
        raise AppError("forbidden", "无权收藏该作品", status_code=403)
    favorites.add(user_id, work_id)
    return {"work_id": work_id, "is_favorite": True}


@router.delete("/{work_id}/favorite")
async def unfavorite_work(
    work_id: int,
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    favorites: FavoriteRepository = Depends(get_favorite_repository),
) -> dict:
    work = works.find_by_id(work_id)
    if work is None:
        raise AppError("work_not_found", "作品不存在", status_code=404)
    if int(work["user_id"]) != user_id:
        raise AppError("forbidden", "无权取消收藏该作品", status_code=403)
    favorites.remove(user_id, work_id)
    return {"work_id": work_id, "is_favorite": False}


@router.post("/{work_id}/share")
async def create_share_payload(
    work_id: int,
    channel: str = Query(...),
    user_id: int = Depends(get_current_user_id),
    works: WorkRepository = Depends(get_work_repository),
    shares: ShareEventRepository = Depends(get_share_event_repository),
) -> dict:
    work = works.find_by_id(work_id)
    if work is None:
        raise AppError("work_not_found", "作品不存在", status_code=404)
    if int(work["user_id"]) != user_id:
        raise AppError("forbidden", "无权分享该作品", status_code=403)
    if channel not in ALLOWED_SHARE_CHANNELS:
        raise AppError("invalid_share_channel", "分享渠道不受支持", status_code=422)
    share_code = secrets.token_hex(6)
    share_event = shares.create(user_id=user_id, work_id=work_id, channel=channel, share_code=share_code)
    link = f"https://huimeng.example.com/?share_code={share_code}&channel={channel}&from_user={user_id}"
    return {
        "share_event": share_event,
        "share_payload": {
            "title": "我在唐绘生成了专属盛唐角色",
            "channel": channel,
            "share_image_url": work["share_image_url"],
            "share_link": link,
        },
    }

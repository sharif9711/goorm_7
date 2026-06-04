from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoResponse

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", response_model=list[VideoResponse])
async def list_videos(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="trend_score"),
):
    order_col = Video.trend_score if sort_by == "trend_score" else Video.view_count
    result = await db.execute(select(Video).order_by(desc(order_col)).limit(limit))
    return result.scalars().all()

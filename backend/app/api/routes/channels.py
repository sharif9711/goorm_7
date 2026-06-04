from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.channel import Channel
from app.models.user import User
from app.schemas.channel import ChannelResponse

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=list[ChannelResponse])
async def list_channels(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="growth_score"),
):
    order_col = Channel.growth_score if sort_by == "growth_score" else Channel.subscriber_count
    result = await db.execute(select(Channel).order_by(desc(order_col)).limit(limit))
    return result.scalars().all()

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.keyword import Keyword
from app.models.user import User
from app.schemas.keyword import KeywordResponse

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("", response_model=list[KeywordResponse])
async def list_keywords(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
):
    result = await db.execute(select(Keyword).order_by(desc(Keyword.trend_score)).limit(limit))
    return result.scalars().all()

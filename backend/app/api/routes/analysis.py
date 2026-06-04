from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisResult,
    HumanReviewRequest,
    TrendOverview,
    WorkflowStatusResponse,
)
from app.services.analysis_service import AnalysisService
from app.services.task_store import task_store
router = APIRouter(tags=["analysis"])
analysis_service = AnalysisService()


@router.get("/trends", response_model=TrendOverview)
async def get_trends(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from app.models.channel import Channel
    from app.models.keyword import Keyword
    from app.models.report import Report
    from app.models.video import Video

    keywords_result = await db.execute(
        select(Keyword).order_by(desc(Keyword.trend_score)).limit(10)
    )
    channels_result = await db.execute(
        select(Channel).order_by(desc(Channel.growth_score)).limit(5)
    )
    videos_result = await db.execute(
        select(Video).order_by(desc(Video.trend_score)).limit(5)
    )
    reports_result = await db.execute(
        select(Report).where(Report.user_id == user.id).order_by(desc(Report.created_at)).limit(5)
    )

    keywords = keywords_result.scalars().all()
    channels = channels_result.scalars().all()
    videos = videos_result.scalars().all()
    reports = reports_result.scalars().all()

    return TrendOverview(
        top_keywords=[{"keyword": k.keyword, "trend_score": k.trend_score, "frequency": k.frequency} for k in keywords],
        rising_channels=[{"title": c.title, "growth_score": c.growth_score, "subscribers": c.subscriber_count} for c in channels],
        rising_videos=[{"title": v.title, "views": v.view_count, "trend_score": v.trend_score} for v in videos],
        recent_analyses=[{"id": r.id, "title": r.title, "created_at": r.created_at.isoformat()} for r in reports],
        content_recommendations=[
            f"'{k.keyword}' 키워드로 콘텐츠 제작 추천" for k in keywords[:3]
        ] if keywords else ["새로운 트렌드 분석을 시작해보세요"],
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task_data = {
        "query": request.query,
        "analysis_type": request.analysis_type,
        "channel_url": request.channel_url,
        "competitor_urls": request.competitor_urls,
        "period": request.period,
        "user_id": user.id,
        "project_id": request.project_id,
    }

    result = await analysis_service.run_analysis(task_data, db)
    status_msg = {
        "completed": "Analysis completed",
        "awaiting_human": "Human review required — please approve or provide feedback",
        "failed": result.get("error", "Analysis failed"),
    }.get(result["status"], result["status"])
    return AnalyzeResponse(
        task_id=result["task_id"],
        status=result["status"],
        message=status_msg,
    )


@router.post("/analyze/{task_id}/resume", response_model=AnalyzeResponse)
async def resume_analysis(
    task_id: str,
    body: HumanReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await analysis_service.resume_analysis(
        task_id, body.approved, body.feedback, db
    )
    status_msg = {
        "completed": "Analysis resumed and completed",
        "rejected": "Analysis rejected by reviewer",
        "failed": result.get("error", "Resume failed"),
    }.get(result["status"], result["status"])
    return AnalyzeResponse(
        task_id=result.get("task_id", task_id),
        status=result["status"],
        message=status_msg,
    )


@router.get("/workflow/{task_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    task_id: str,
    user: User = Depends(get_current_user),
):
    result = await task_store.get_task(task_id)
    if not result:
        state = await analysis_service.orchestrator.get_workflow_state(task_id)
        if not state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        result = state

    interrupt_payload = None
    if result.get("status") == "awaiting_human":
        interrupt_payload = {
            "message": "분석 결과를 검토해주세요.",
            "quality_score": result.get("quality_score", 0),
            "insights_preview": result.get("insights", [])[:5],
        }

    return WorkflowStatusResponse(
        task_id=result.get("task_id", task_id),
        status=result.get("status", "unknown"),
        current_step=result.get("current_step"),
        steps_completed=result.get("steps_completed", []),
        requires_human_review=result.get("requires_human_review", False),
        quality_score=result.get("quality_score", 0),
        evaluation=result.get("evaluation", {}),
        interrupt_payload=interrupt_payload,
    )


@router.get("/analyze/{task_id}", response_model=AnalysisResult)
async def get_analysis_result(
    task_id: str,
    user: User = Depends(get_current_user),
):
    result = await task_store.get_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return AnalysisResult(
        task_id=result.get("task_id", task_id),
        status=result.get("status", "unknown"),
        query=result.get("query", ""),
        analysis_type=result.get("analysis_type", ""),
        plan=result.get("plan", []),
        steps_completed=result.get("steps_completed", []),
        tool_calls=result.get("tool_calls", []),
        data=result.get("data", {}),
        insights=result.get("insights", []),
        content_ideas=result.get("content_ideas", {}),
        quality_score=result.get("quality_score", 0),
        evaluation=result.get("evaluation", {}),
        requires_human_review=result.get("requires_human_review", False),
        report_id=result.get("report_id"),
        created_at=result.get("created_at"),
    )

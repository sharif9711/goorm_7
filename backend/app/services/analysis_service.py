from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.keyword import Keyword
from app.models.report import Report
from app.models.video import Video
from app.orchestrator.orchestrator import AgentOrchestrator
from app.services.rag import RAGService
from app.services.task_store import task_store


class AnalysisService:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.rag = RAGService()

    async def run_analysis(self, request: dict, db: AsyncSession) -> dict:
        result = await self.orchestrator.run_analysis(request)

        if result["status"] == "completed":
            await self._persist_results(db, result, request.get("user_id"))
            report_data = result.get("report", {})
            if report_data and request.get("user_id"):
                report = Report(
                    user_id=request["user_id"],
                    project_id=request.get("project_id"),
                    title=report_data.get("title", "Trend Report"),
                    summary=report_data.get("summary"),
                    markdown_content=report_data.get("markdown_content"),
                    analysis_type=request.get("analysis_type", "keyword_search"),
                )
                db.add(report)
                await db.flush()
                result["report_id"] = report.id

                if report_data.get("markdown_content"):
                    await self.rag.index_content(
                        db, "report", str(report.id), report_data["markdown_content"]
                    )

        await task_store.set_task(result["task_id"], result)
        return result

    async def resume_analysis(
        self,
        task_id: str,
        approved: bool,
        feedback: str | None,
        db: AsyncSession,
    ) -> dict:
        result = await self.orchestrator.resume_analysis(task_id, approved, feedback)

        if result["status"] == "completed":
            existing = await task_store.get_task(task_id)
            user_id = existing.get("user_id") if existing else None
            await self._persist_results(db, result, user_id)
            report_data = result.get("report", {})
            if report_data and user_id:
                report = Report(
                    user_id=user_id,
                    project_id=existing.get("project_id") if existing else None,
                    title=report_data.get("title", "Trend Report"),
                    summary=report_data.get("summary"),
                    markdown_content=report_data.get("markdown_content"),
                    analysis_type=result.get("analysis_type", "keyword_search"),
                )
                db.add(report)
                await db.flush()
                result["report_id"] = report.id
                if report_data.get("markdown_content"):
                    await self.rag.index_content(
                        db, "report", str(report.id), report_data["markdown_content"]
                    )

        await task_store.set_task(task_id, result)
        return result

    async def _persist_results(self, db: AsyncSession, result: dict, user_id: int | None) -> None:
        data = result.get("data", {})

        for ch in data.get("channels", []):
            existing = await db.execute(
                select(Channel).where(Channel.channel_id == ch["channel_id"])
            )
            channel = existing.scalar_one_or_none()
            growth = next(
                (ca["growth_score"] for ca in data.get("channel_analyses", [])
                 if ca["channel_id"] == ch["channel_id"]),
                0,
            )
            if channel:
                channel.title = ch.get("title", channel.title)
                channel.subscriber_count = ch.get("subscriber_count", 0)
                channel.video_count = ch.get("video_count", 0)
                channel.view_count = ch.get("view_count", 0)
                channel.growth_score = growth
            else:
                db.add(Channel(
                    channel_id=ch["channel_id"],
                    title=ch.get("title", ""),
                    description=ch.get("description"),
                    subscriber_count=ch.get("subscriber_count", 0),
                    video_count=ch.get("video_count", 0),
                    view_count=ch.get("view_count", 0),
                    growth_score=growth,
                ))

        for video in data.get("videos", []):
            existing = await db.execute(
                select(Video).where(Video.video_id == video["video_id"])
            )
            v = existing.scalar_one_or_none()
            if v:
                v.view_count = video.get("view_count", 0)
                v.like_count = video.get("like_count", 0)
                v.comment_count = video.get("comment_count", 0)
            else:
                import json
                db.add(Video(
                    video_id=video["video_id"],
                    channel_id=video.get("channel_id", ""),
                    title=video.get("title", ""),
                    description=video.get("description"),
                    view_count=video.get("view_count", 0),
                    like_count=video.get("like_count", 0),
                    comment_count=video.get("comment_count", 0),
                    thumbnail_url=video.get("thumbnail_url"),
                    tags=json.dumps(video.get("tags", [])),
                ))

        for kw in data.get("keywords", []):
            existing = await db.execute(
                select(Keyword).where(Keyword.keyword == kw["keyword"])
            )
            keyword = existing.scalar_one_or_none()
            if keyword:
                keyword.frequency = kw.get("frequency", 0)
                keyword.growth_rate = kw.get("growth_rate", 0)
                keyword.competition_score = kw.get("competition_score", 0)
                keyword.trend_score = kw.get("trend_score", 0)
            else:
                db.add(Keyword(
                    keyword=kw["keyword"],
                    frequency=kw.get("frequency", 0),
                    growth_rate=kw.get("growth_rate", 0),
                    competition_score=kw.get("competition_score", 0),
                    trend_score=kw.get("trend_score", 0),
                ))

from __future__ import annotations

import asyncio

from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.run_analysis_task")
def run_analysis_task(request_data: dict) -> dict:
    from app.core.database import AsyncSessionLocal
    from app.services.analysis_service import AnalysisService

    async def _run():
        async with AsyncSessionLocal() as db:
            service = AnalysisService()
            return await service.run_analysis(request_data, db)

    return asyncio.run(_run())


@celery_app.task(name="app.workers.tasks.generate_weekly_report")
def generate_weekly_report() -> dict:
    """Generate weekly trend report every Monday."""
    from app.core.database import AsyncSessionLocal
    from app.services.analysis_service import AnalysisService

    async def _run():
        async with AsyncSessionLocal() as db:
            service = AnalysisService()
            return await service.run_analysis(
                {
                    "query": "AI technology trends",
                    "analysis_type": "full",
                    "period": "7d",
                    "user_id": 1,
                },
                db,
            )

    return asyncio.run(_run())

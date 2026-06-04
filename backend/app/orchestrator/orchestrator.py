from __future__ import annotations

from typing import Any

from app.graph.workflow import TrendResearchWorkflow


class AgentOrchestrator:
    """LangGraph-powered orchestrator (replaces sequential pipeline)."""

    def __init__(self):
        self.workflow = TrendResearchWorkflow()

    async def run_analysis(self, request: dict[str, Any]) -> dict[str, Any]:
        return await self.workflow.run(request)

    async def resume_analysis(
        self,
        task_id: str,
        approved: bool,
        feedback: str | None = None,
    ) -> dict[str, Any]:
        return await self.workflow.resume(task_id, approved, feedback)

    async def get_workflow_state(self, task_id: str) -> dict[str, Any] | None:
        return await self.workflow.get_workflow_state(task_id)

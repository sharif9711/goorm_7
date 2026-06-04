from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from app.graph.nodes import GraphNodes
from app.graph.state import AgentGraphState
from app.services.agent_memory import AgentMemoryService


def _route_after_critic(state: AgentGraphState) -> Literal["human_review", "report"]:
    if state.get("requires_human_review"):
        return "human_review"
    return "report"


def _route_after_human_review(state: AgentGraphState) -> Literal["report", "__end__"]:
    if state.get("status") == "rejected":
        return "__end__"
    return "report"


class TrendResearchWorkflow:
    """LangGraph workflow with tool calling, memory, HITL, and evaluation."""

    def __init__(self):
        self.nodes = GraphNodes()
        self.memory_service = AgentMemoryService()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentGraphState)

        graph.add_node("planner", self.nodes.planner_node)
        graph.add_node("collector", self.nodes.collector_node)
        graph.add_node("analysis", self.nodes.analysis_node)
        graph.add_node("insights", self.nodes.insight_node)
        graph.add_node("critic", self.nodes.critic_node)
        graph.add_node("human_review", self.nodes.human_review_node)
        graph.add_node("report", self.nodes.report_node)
        graph.add_node("evaluation", self.nodes.evaluation_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "collector")
        graph.add_edge("collector", "analysis")
        graph.add_edge("analysis", "insights")
        graph.add_edge("insights", "critic")
        graph.add_conditional_edges("critic", _route_after_critic, {"human_review": "human_review", "report": "report"})
        graph.add_conditional_edges("human_review", _route_after_human_review, {"report": "report", "__end__": END})
        graph.add_edge("report", "evaluation")
        graph.add_edge("evaluation", END)

        return graph.compile(checkpointer=self.checkpointer)

    async def run(self, request: dict[str, Any]) -> dict[str, Any]:
        task_id = str(uuid.uuid4())
        initial_state: AgentGraphState = {
            "task_id": task_id,
            "query": request.get("query", ""),
            "analysis_type": request.get("analysis_type", "keyword_search"),
            "channel_url": request.get("channel_url"),
            "competitor_urls": request.get("competitor_urls", []),
            "period": request.get("period", "7d"),
            "user_id": request.get("user_id"),
            "project_id": request.get("project_id"),
            "status": "running",
            "steps_completed": [],
            "tool_calls": [],
            "memory_context": [],
            "human_approved": None,
            "human_feedback": None,
            "requires_human_review": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        config = {"configurable": {"thread_id": task_id}}

        try:
            final_state = await self.graph.ainvoke(initial_state, config)
            snapshot = await self.graph.aget_state(config)
            if snapshot.next:
                merged = dict(snapshot.values) if snapshot.values else final_state
                merged["status"] = "awaiting_human"
                return self._build_response(merged)

            final_state["status"] = "completed"
            await self._save_memory(final_state)
            return self._build_response(final_state)
        except Exception as e:
            initial_state["status"] = "failed"
            initial_state["error"] = str(e)
            return self._build_response(initial_state)

    async def resume(
        self,
        task_id: str,
        approved: bool,
        feedback: str | None = None,
    ) -> dict[str, Any]:
        config = {"configurable": {"thread_id": task_id}}

        if not approved:
            return self._build_response({
                "task_id": task_id,
                "status": "rejected",
                "human_approved": False,
                "human_feedback": feedback,
                "error": feedback or "Rejected by human reviewer",
            })

        try:
            final_state = await self.graph.ainvoke(
                Command(resume={"approved": True, "feedback": feedback or ""}),
                config,
            )
            snapshot = await self.graph.aget_state(config)
            if snapshot.next:
                merged = dict(snapshot.values) if snapshot.values else final_state
                merged["status"] = "awaiting_human"
                return self._build_response(merged)
            final_state["status"] = "completed"
            await self._save_memory(final_state)
            return self._build_response(final_state)
        except Exception as e:
            return self._build_response({
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
            })

    async def get_workflow_state(self, task_id: str) -> dict[str, Any] | None:
        config = {"configurable": {"thread_id": task_id}}
        try:
            snapshot = await self.graph.aget_state(config)
            if snapshot and snapshot.values:
                return self._build_response(dict(snapshot.values))
        except Exception:
            pass
        return None

    async def _save_memory(self, state: AgentGraphState) -> None:
        user_id = state.get("user_id")
        if not user_id:
            return
        summary = (state.get("report") or {}).get("summary") or state.get("query", "")
        keywords = [k.get("keyword", "") for k in state.get("keywords", [])[:5]]
        await self.memory_service.add_analysis_memory(
            user_id=user_id,
            task_id=state.get("task_id", ""),
            query=state.get("query", ""),
            analysis_type=state.get("analysis_type", ""),
            summary=summary,
            keywords=keywords,
        )

    def _build_response(self, state: dict[str, Any]) -> dict[str, Any]:
        report = state.get("report", {})
        return {
            "task_id": state.get("task_id"),
            "status": state.get("status"),
            "query": state.get("query"),
            "analysis_type": state.get("analysis_type"),
            "user_id": state.get("user_id"),
            "project_id": state.get("project_id"),
            "current_step": state.get("current_step"),
            "plan": state.get("plan", []),
            "steps_completed": state.get("steps_completed", []),
            "tool_calls": state.get("tool_calls", []),
            "memory_context": state.get("memory_context", []),
            "requires_human_review": state.get("requires_human_review", False),
            "human_feedback": state.get("human_feedback"),
            "evaluation": state.get("evaluation", {}),
            "data": {
                "videos": state.get("videos", [])[:20],
                "channels": state.get("channels", [])[:10],
                "channel_analyses": state.get("channel_analyses", []),
                "keywords": state.get("keywords", []),
                "title_patterns": state.get("title_patterns", []),
                "title_structures": state.get("title_structures", []),
                "thumbnail_analysis": state.get("thumbnail_analysis", {}),
                "gap_analysis": state.get("gap_analysis", {}),
                "user_channel": state.get("user_channel"),
                "competitors": state.get("competitors", []),
            },
            "insights": state.get("insights", []),
            "content_ideas": state.get("content_ideas", {}),
            "quality_score": state.get("quality_score", 0),
            "report": report,
            "error": state.get("error"),
            "created_at": state.get("created_at"),
        }

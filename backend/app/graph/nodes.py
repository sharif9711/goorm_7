from __future__ import annotations

from typing import Any

from langgraph.types import interrupt

from app.agents.channel_intelligence import ChannelIntelligenceAgent
from app.agents.competitor import CompetitorAgent
from app.agents.critic import CriticAgent
from app.agents.evaluation import EvaluationAgent
from app.agents.insight_generator import InsightGeneratorAgent
from app.agents.keyword_intelligence import KeywordIntelligenceAgent
from app.agents.report import ReportAgent
from app.agents.thumbnail_vision import ThumbnailVisionAgent
from app.agents.title_pattern import TitlePatternAgent
from app.agents.trend_collector import TrendCollectorAgent
from app.graph.state import AgentGraphState
from app.graph.tool_runner import OpenAIToolRunner
from app.services.agent_memory import AgentMemoryService
from app.services.openai_service import OpenAIService
from app.services.youtube import YouTubeService


class GraphNodes:
    """LangGraph node implementations wrapping existing agents."""

    ANALYSIS_NODES = {
        "channel_intelligence",
        "keyword_intelligence",
        "title_pattern",
        "thumbnail_vision",
        "competitor",
    }

    def __init__(self):
        youtube = YouTubeService()
        openai = OpenAIService()
        self.tool_runner = OpenAIToolRunner(openai)
        self.memory = AgentMemoryService()
        self.agents = {
            "trend_collector": TrendCollectorAgent(youtube),
            "channel_intelligence": ChannelIntelligenceAgent(),
            "keyword_intelligence": KeywordIntelligenceAgent(),
            "title_pattern": TitlePatternAgent(),
            "thumbnail_vision": ThumbnailVisionAgent(openai),
            "competitor": CompetitorAgent(youtube),
            "insight_generator": InsightGeneratorAgent(openai),
            "critic": CriticAgent(),
            "report": ReportAgent(openai),
            "evaluation": EvaluationAgent(),
        }

    async def planner_node(self, state: AgentGraphState) -> dict[str, Any]:
        memory = state.get("memory_context") or []
        if state.get("user_id") and not memory:
            memory = await self.memory.get_user_memory(state["user_id"])

        result = await self.tool_runner.run_planner_with_tools(
            state.get("query", ""),
            state.get("analysis_type", "keyword_search"),
            memory,
        )
        return {
            "plan": result.get("plan", []),
            "tool_calls": result.get("tool_calls", []),
            "memory_context": memory,
            "current_step": "planner",
            "steps_completed": ["planner"],
        }

    async def collector_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        result = await self.agents["trend_collector"].run(ctx)
        return {
            **result,
            "current_step": "trend_collector",
            "steps_completed": ["trend_collector"],
        }

    async def analysis_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        analysis_type = state.get("analysis_type", "keyword_search")
        updates: dict[str, Any] = {"current_step": "analysis", "steps_completed": []}

        node_map = {
            "keyword_search": ["channel_intelligence", "keyword_intelligence", "title_pattern"],
            "trending": ["channel_intelligence", "keyword_intelligence"],
            "channel": ["channel_intelligence"],
            "competitor": ["channel_intelligence", "competitor", "keyword_intelligence"],
            "title": ["title_pattern"],
            "thumbnail": ["thumbnail_vision"],
            "content_ideas": ["keyword_intelligence", "title_pattern"],
            "full": [
                "channel_intelligence", "keyword_intelligence", "title_pattern",
                "thumbnail_vision", "competitor",
            ],
        }
        for agent_name in node_map.get(analysis_type, node_map["keyword_search"]):
            result = await self.agents[agent_name].run(ctx)
            ctx.update(result)
            updates.update(result)
            updates["steps_completed"].append(agent_name)

        return updates

    async def insight_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        result = await self.agents["insight_generator"].run(ctx)
        return {
            **result,
            "current_step": "insight_generator",
            "steps_completed": ["insight_generator"],
        }

    async def critic_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        result = await self.agents["critic"].run(ctx)
        quality = result.get("quality_score", 0)
        analysis_type = state.get("analysis_type", "")
        requires_review = quality < 70 or analysis_type in ("full", "competitor")
        return {
            **result,
            "requires_human_review": requires_review,
            "current_step": "critic",
            "steps_completed": ["critic"],
        }

    async def human_review_node(self, state: AgentGraphState) -> dict[str, Any]:
        if not state.get("requires_human_review"):
            return {"current_step": "human_review", "steps_completed": ["human_review_skipped"]}

        if state.get("human_approved") is None:
            review_payload = interrupt({
                "type": "human_review",
                "message": "분석 결과를 검토해주세요. 승인 또는 수정 피드백을 제공하세요.",
                "quality_score": state.get("quality_score", 0),
                "insights_preview": state.get("insights", [])[:5],
                "query": state.get("query", ""),
            })
            approved = review_payload.get("approved", False) if isinstance(review_payload, dict) else bool(review_payload)
            feedback = review_payload.get("feedback", "") if isinstance(review_payload, dict) else str(review_payload or "")

            if not approved:
                return {
                    "status": "rejected",
                    "human_approved": False,
                    "human_feedback": feedback,
                    "error": feedback or "Rejected by human reviewer",
                    "current_step": "human_review",
                    "steps_completed": ["human_review_rejected"],
                }

            updates: dict[str, Any] = {
                "status": "running",
                "human_approved": True,
                "human_feedback": feedback,
                "current_step": "human_review",
                "steps_completed": ["human_review_approved"],
            }
            if feedback and state.get("insights"):
                updates["insights"] = state["insights"] + [f"[Human feedback] {feedback}"]
            return updates

        feedback = state.get("human_feedback") or ""
        updates: dict[str, Any] = {
            "status": "running",
            "current_step": "human_review",
            "steps_completed": ["human_review"],
        }
        if feedback and state.get("insights"):
            updates["insights"] = state["insights"] + [f"[Human feedback] {feedback}"]
        return updates

    async def report_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        result = await self.agents["report"].run(ctx)
        return {
            **result,
            "current_step": "report",
            "steps_completed": ["report"],
        }

    async def evaluation_node(self, state: AgentGraphState) -> dict[str, Any]:
        ctx = dict(state)
        result = await self.agents["evaluation"].run(ctx)
        return {
            **result,
            "current_step": "evaluation",
            "steps_completed": ["evaluation"],
        }

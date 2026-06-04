from __future__ import annotations

import pytest

from app.agents.evaluation import EvaluationAgent
from app.graph.state import AgentGraphState


@pytest.mark.asyncio
async def test_evaluation_agent():
    agent = EvaluationAgent()
    result = await agent.run({
        "insights": ["Valid insight about AI trends", "Another useful insight"],
        "quality_score": 75,
        "videos": [{}],
        "keywords": [{}],
        "plan": ["step1"],
        "report": {"title": "Test"},
    })
    assert "evaluation" in result
    assert result["evaluation"]["overall_score"] > 0
    assert "passed" in result["evaluation"]


def test_agent_graph_state_keys():
    state: AgentGraphState = {
        "task_id": "test",
        "query": "AI",
        "analysis_type": "full",
        "status": "running",
    }
    assert state["query"] == "AI"


def test_route_after_critic():
    from app.graph.workflow import _route_after_critic

    assert _route_after_critic({"requires_human_review": True}) == "human_review"
    assert _route_after_critic({"requires_human_review": False}) == "report"

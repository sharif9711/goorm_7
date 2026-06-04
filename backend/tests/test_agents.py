from __future__ import annotations

import pytest
from app.agents.keyword_intelligence import KeywordIntelligenceAgent
from app.agents.planner import PlannerAgent
from app.agents.title_pattern import TitlePatternAgent
from app.agents.critic import CriticAgent


@pytest.mark.asyncio
async def test_planner_agent():
    agent = PlannerAgent()
    result = await agent.run({"query": "AI Automation", "analysis_type": "keyword_search"})
    assert "plan" in result
    assert len(result["plan"]) > 0


@pytest.mark.asyncio
async def test_keyword_intelligence_agent():
    agent = KeywordIntelligenceAgent()
    videos = [
        {"title": "AI Automation Guide 2026", "description": "Learn AI automation", "tags": ["AI", "automation"]},
        {"title": "Best AI Tools", "description": "Top AI tools for creators", "tags": ["AI", "tools"]},
    ]
    result = await agent.run({"videos": videos, "query": "AI"})
    assert "keywords" in result
    assert len(result["keywords"]) > 0


@pytest.mark.asyncio
async def test_title_pattern_agent():
    agent = TitlePatternAgent()
    videos = [
        {"title": "충격! AI가 바꿔버렸다"},
        {"title": "5가지 AI 자동화 방법"},
        {"title": "AI vs Human - Who Wins?"},
    ]
    result = await agent.run({"videos": videos})
    assert "title_patterns" in result


@pytest.mark.asyncio
async def test_critic_agent():
    agent = CriticAgent()
    result = await agent.run({
        "insights": ["Valid insight about trends", "Valid insight about trends", "Short"],
        "content_ideas": {"shorts": ["idea1", "idea1", "idea2"]},
        "videos": [{}],
        "keywords": [{}],
    })
    assert result["quality_score"] > 0
    assert len(result["insights"]) <= 2

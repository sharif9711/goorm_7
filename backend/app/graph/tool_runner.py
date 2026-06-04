from __future__ import annotations

import json
from typing import Any

from app.core.config import get_settings
from app.graph.tools import OPENAI_TOOL_DEFINITIONS, execute_tool
from app.services.openai_service import OpenAIService

settings = get_settings()


class OpenAIToolRunner:
    """OpenAI Agents SDK-style tool calling loop for the Planner agent."""

    def __init__(self, openai: OpenAIService | None = None):
        self.openai = openai or OpenAIService()

    async def run_planner_with_tools(
        self,
        query: str,
        analysis_type: str,
        memory_context: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not self.openai.client:
            return self._fallback_plan(query, analysis_type)

        memory_text = ""
        if memory_context:
            memory_text = "\n".join(
                f"- {m.get('query')}: {m.get('summary', '')}" for m in memory_context[:5]
            )

        system = (
            "You are the Planner Agent for a YouTube trend research platform. "
            "Use available tools to gather initial data, then output a JSON plan. "
            "Respond with final JSON: {\"plan\": [\"step1\", ...], \"tool_summary\": \"brief summary\"}"
        )
        user_msg = (
            f"Query: {query}\nAnalysis type: {analysis_type}\n"
            f"Past analyses:\n{memory_text or 'None'}\n"
            "Call tools if needed, then provide the analysis plan."
        )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]
        tool_calls_log: list[dict[str, Any]] = []

        for _ in range(5):
            response = await self.openai.client.chat.completions.create(
                model=self.openai.model,
                messages=messages,
                tools=OPENAI_TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.3,
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg.model_dump())
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = execute_tool(tc.function.name, args)
                    tool_calls_log.append({
                        "tool": tc.function.name,
                        "arguments": args,
                        "result_preview": result[:500],
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                continue

            content = msg.content or "{}"
            try:
                if "{" in content:
                    json_str = content[content.index("{"): content.rindex("}") + 1]
                    parsed = json.loads(json_str)
                else:
                    parsed = {"plan": content.split("\n"), "tool_summary": ""}
            except json.JSONDecodeError:
                parsed = self._fallback_plan(query, analysis_type)

            parsed["tool_calls"] = tool_calls_log
            return parsed

        return self._fallback_plan(query, analysis_type)

    def _fallback_plan(self, query: str, analysis_type: str) -> dict[str, Any]:
        from app.agents.planner import PlannerAgent

        base = PlannerAgent.ANALYSIS_PLANS.get(analysis_type, PlannerAgent.ANALYSIS_PLANS["keyword_search"])
        return {
            "plan": [f"'{query}' — {step}" for step in base],
            "tool_summary": "Fallback plan (no OpenAI tool loop)",
            "tool_calls": [],
        }

from __future__ import annotations

import json
from typing import Any, Callable

from app.services.youtube import YouTubeService

_youtube = YouTubeService()


def search_youtube_videos(query: str, max_results: int = 25, order: str = "relevance") -> str:
    """Search YouTube videos by keyword and return JSON results."""
    videos = _youtube.search_videos(query, max_results=max_results, order=order)
    return json.dumps(videos[:max_results], ensure_ascii=False, default=str)


def get_trending_videos(region_code: str = "KR", max_results: int = 25) -> str:
    """Fetch trending/popular YouTube videos for a region."""
    videos = _youtube.get_trending_videos(region_code=region_code, max_results=max_results)
    return json.dumps(videos, ensure_ascii=False, default=str)


def get_channel_info(channel_url_or_id: str) -> str:
    """Get YouTube channel metadata from URL or channel ID."""
    channel_id = _youtube.extract_channel_id(channel_url_or_id) or channel_url_or_id
    channel = _youtube.get_channel(channel_id)
    if not channel:
        return json.dumps({"error": "Channel not found"})
    return json.dumps(channel, ensure_ascii=False, default=str)


def get_channel_videos(channel_url_or_id: str, max_results: int = 25) -> str:
    """List recent videos from a YouTube channel."""
    channel_id = _youtube.extract_channel_id(channel_url_or_id) or channel_url_or_id
    videos = _youtube.get_channel_videos(channel_id, max_results=max_results)
    return json.dumps(videos, ensure_ascii=False, default=str)


OPENAI_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_youtube_videos",
            "description": "Search YouTube videos by keyword query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword"},
                    "max_results": {"type": "integer", "default": 25},
                    "order": {"type": "string", "enum": ["relevance", "viewCount", "date"], "default": "relevance"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_trending_videos",
            "description": "Get trending YouTube videos for a region",
            "parameters": {
                "type": "object",
                "properties": {
                    "region_code": {"type": "string", "default": "KR"},
                    "max_results": {"type": "integer", "default": 25},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_info",
            "description": "Get YouTube channel metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_url_or_id": {"type": "string"},
                },
                "required": ["channel_url_or_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_channel_videos",
            "description": "List videos from a YouTube channel",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel_url_or_id": {"type": "string"},
                    "max_results": {"type": "integer", "default": 25},
                },
                "required": ["channel_url_or_id"],
            },
        },
    },
]

TOOL_REGISTRY: dict[str, Callable[..., str]] = {
    "search_youtube_videos": search_youtube_videos,
    "get_trending_videos": get_trending_videos,
    "get_channel_info": get_channel_info,
    "get_channel_videos": get_channel_videos,
}


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    fn = TOOL_REGISTRY.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    return fn(**arguments)

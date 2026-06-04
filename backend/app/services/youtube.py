from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from googleapiclient.discovery import build

from app.core.config import get_settings

settings = get_settings()


class YouTubeService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self._youtube = None

    @property
    def youtube(self):
        if self._youtube is None:
            if not self.api_key:
                raise ValueError("YOUTUBE_API_KEY is not configured")
            self._youtube = build("youtube", "v3", developerKey=self.api_key, cache_discovery=False)
        return self._youtube

    def extract_channel_id(self, url: str) -> str | None:
        patterns = [
            r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
            r"youtube\.com/@([a-zA-Z0-9_.-]+)",
            r"youtube\.com/c/([a-zA-Z0-9_.-]+)",
            r"youtube\.com/user/([a-zA-Z0-9_.-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                handle = match.group(1)
                if pattern.startswith(r"youtube\.com/channel"):
                    return handle
                return self.resolve_channel_handle(handle)
        if url.startswith("UC") and len(url) >= 20:
            return url
        return None

    def resolve_channel_handle(self, handle: str) -> str | None:
        try:
            request = self.youtube.search().list(
                part="snippet", q=handle, type="channel", maxResults=1
            )
            response = request.execute()
            items = response.get("items", [])
            if items:
                return items[0]["snippet"]["channelId"]
        except Exception:
            pass
        return None

    def search_videos(
        self, query: str, max_results: int = 25, order: str = "relevance"
    ) -> list[dict[str, Any]]:
        try:
            search_response = (
                self.youtube.search()
                .list(part="snippet", q=query, type="video", maxResults=max_results, order=order)
                .execute()
            )
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            if not video_ids:
                return []
            return self._get_video_details(video_ids)
        except Exception as e:
            raise RuntimeError(f"YouTube search failed: {e}") from e

    def get_trending_videos(self, region_code: str = "KR", max_results: int = 25) -> list[dict[str, Any]]:
        try:
            response = (
                self.youtube.videos()
                .list(part="snippet,statistics,contentDetails", chart="mostPopular", regionCode=region_code, maxResults=max_results)
                .execute()
            )
            return [self._parse_video(item) for item in response.get("items", [])]
        except Exception as e:
            raise RuntimeError(f"YouTube trending failed: {e}") from e

    def get_channel(self, channel_id: str) -> dict[str, Any] | None:
        try:
            response = (
                self.youtube.channels()
                .list(part="snippet,statistics,contentDetails", id=channel_id)
                .execute()
            )
            items = response.get("items", [])
            if not items:
                return None
            item = items[0]
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            return {
                "channel_id": channel_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            }
        except Exception:
            return None

    def get_channel_videos(self, channel_id: str, max_results: int = 25) -> list[dict[str, Any]]:
        try:
            channel_response = (
                self.youtube.channels()
                .list(part="contentDetails", id=channel_id)
                .execute()
            )
            items = channel_response.get("items", [])
            if not items:
                return []
            uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
            playlist_response = (
                self.youtube.playlistItems()
                .list(part="snippet", playlistId=uploads_id, maxResults=max_results)
                .execute()
            )
            video_ids = [
                item["snippet"]["resourceId"]["videoId"]
                for item in playlist_response.get("items", [])
            ]
            return self._get_video_details(video_ids)
        except Exception:
            return []

    def _get_video_details(self, video_ids: list[str]) -> list[dict[str, Any]]:
        if not video_ids:
            return []
        response = (
            self.youtube.videos()
            .list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
            .execute()
        )
        return [self._parse_video(item) for item in response.get("items", [])]

    def _parse_video(self, item: dict[str, Any]) -> dict[str, Any]:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        published = snippet.get("publishedAt")
        published_at = None
        if published:
            published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))

        tags = snippet.get("tags", [])
        return {
            "video_id": item["id"],
            "channel_id": snippet.get("channelId", ""),
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "published_at": published_at.isoformat() if published_at else None,
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "tags": tags,
        }

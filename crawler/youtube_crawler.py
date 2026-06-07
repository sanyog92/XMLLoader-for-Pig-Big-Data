"""
Discovers FIFA 2026 / viral football content on YouTube.

Returns a list of VideoMeta dicts that the downloader can act on.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

import yt_dlp
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import (
    FIFA_SEARCH_KEYWORDS,
    YOUTUBE_SOURCE_CHANNELS,
    MAX_SOURCE_DURATION,
)
from utils.logger import logger
from utils.helpers import sha256_id


@dataclass
class VideoMeta:
    id: str
    url: str
    title: str
    channel: str
    duration: float
    view_count: int
    like_count: int
    upload_date: str
    description: str = ""
    thumbnail_url: str = ""
    tags: list[str] = field(default_factory=list)
    # viral score computed locally
    viral_score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class YouTubeCrawler:
    """Searches YouTube for FIFA 2026 highlights and viral football clips."""

    _YDL_OPTS_BASE = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
    }

    def __init__(self, max_results_per_query: int = 20):
        self.max_results_per_query = max_results_per_query
        self._seen: set[str] = set()

    # ── Public API ────────────────────────────────────────────

    def discover(self) -> list[VideoMeta]:
        """Run all discovery strategies and return deduplicated results."""
        results: list[VideoMeta] = []
        results += self._search_keywords()
        results += self._scan_channels()
        deduped = self._deduplicate(results)
        ranked = self._rank(deduped)
        logger.info(f"YouTube crawler found {len(ranked)} unique candidates")
        return ranked

    # ── Internal strategies ──────────────────────────────────

    def _search_keywords(self) -> list[VideoMeta]:
        videos: list[VideoMeta] = []
        for kw in FIFA_SEARCH_KEYWORDS:
            try:
                batch = self._yt_search(kw)
                videos.extend(batch)
                logger.debug(f"Keyword '{kw}' → {len(batch)} results")
            except Exception as exc:
                logger.warning(f"Keyword search failed for '{kw}': {exc}")
        return videos

    def _scan_channels(self) -> list[VideoMeta]:
        videos: list[VideoMeta] = []
        for channel_id in YOUTUBE_SOURCE_CHANNELS:
            try:
                url = f"https://www.youtube.com/channel/{channel_id}/videos"
                batch = self._yt_extract_playlist(url)
                videos.extend(batch)
                logger.debug(f"Channel {channel_id} → {len(batch)} videos")
            except Exception as exc:
                logger.warning(f"Channel scan failed for {channel_id}: {exc}")
        return videos

    # ── yt-dlp helpers ────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    def _yt_search(self, query: str) -> list[VideoMeta]:
        search_url = f"ytsearch{self.max_results_per_query}:{query}"
        opts = {
            **self._YDL_OPTS_BASE,
            "extract_flat": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
        entries = (info or {}).get("entries", [])
        return [self._entry_to_meta(e) for e in entries if e and self._is_eligible(e)]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    def _yt_extract_playlist(self, url: str) -> list[VideoMeta]:
        opts = {
            **self._YDL_OPTS_BASE,
            "playlistend": self.max_results_per_query,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = (info or {}).get("entries", [])
        return [self._entry_to_meta(e) for e in entries if e and self._is_eligible(e)]

    # ── Helpers ───────────────────────────────────────────────

    def _is_eligible(self, entry: dict) -> bool:
        duration = entry.get("duration") or 0
        if duration > MAX_SOURCE_DURATION:
            return False
        title = (entry.get("title") or "").lower()
        # Prefer match-related content
        keywords = ["goal", "highlight", "world cup", "fifa", "2026", "match", "viral"]
        return any(kw in title for kw in keywords)

    @staticmethod
    def _entry_to_meta(entry: dict) -> VideoMeta:
        vid_id = entry.get("id") or sha256_id(entry.get("url", ""))
        return VideoMeta(
            id=vid_id,
            url=entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}",
            title=entry.get("title", ""),
            channel=entry.get("uploader") or entry.get("channel", ""),
            duration=float(entry.get("duration") or 0),
            view_count=int(entry.get("view_count") or 0),
            like_count=int(entry.get("like_count") or 0),
            upload_date=entry.get("upload_date", ""),
            description=entry.get("description", "")[:500],
            thumbnail_url=entry.get("thumbnail", ""),
            tags=entry.get("tags") or [],
        )

    @staticmethod
    def _rank(videos: list[VideoMeta]) -> list[VideoMeta]:
        """Compute a viral score and sort descending."""
        for v in videos:
            view_weight = min(v.view_count / 1_000_000, 10)
            like_ratio = (v.like_count / max(v.view_count, 1)) * 100
            v.viral_score = round(view_weight * 0.6 + like_ratio * 0.4, 4)
        return sorted(videos, key=lambda v: v.viral_score, reverse=True)

    def _deduplicate(self, videos: list[VideoMeta]) -> list[VideoMeta]:
        unique: list[VideoMeta] = []
        for v in videos:
            if v.id not in self._seen:
                self._seen.add(v.id)
                unique.append(v)
        return unique

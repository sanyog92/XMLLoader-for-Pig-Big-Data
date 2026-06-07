"""
Crawls sports news RSS feeds and pages for FIFA 2026 trending stories.
Returns plain text summaries used by the AI caption generator.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import logger

RSS_FEEDS = [
    "https://www.goal.com/en/rss/feeds",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://rss.foxsports.com/rss/world-soccer.xml",
    "https://www.skysports.com/rss/12040",          # Sky Sports Football
    "https://api.foxsports.com/v1/rss?partnerKey=zBaFxRyJ&tag=soccer",
]

FIFA_KEYWORDS = {
    "world cup", "copa mundial", "fifa 2026", "worldcup", "fifaworldcup",
    "qatar", "usa 2026", "canada", "mexico",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str
    source: str
    published: str = ""


class NewsCrawler:
    """Fetches FIFA 2026 related news from RSS feeds."""

    def __init__(self, max_items_per_feed: int = 10):
        self.max_items = max_items_per_feed

    def discover(self) -> list[NewsItem]:
        items: list[NewsItem] = []
        for feed_url in RSS_FEEDS:
            try:
                batch = self._parse_feed(feed_url)
                items.extend(batch)
                logger.debug(f"RSS {feed_url} → {len(batch)} items")
            except Exception as exc:
                logger.warning(f"RSS feed failed {feed_url}: {exc}")
        filtered = [i for i in items if self._is_relevant(i)]
        logger.info(f"News crawler found {len(filtered)} relevant articles")
        return filtered

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20))
    def _parse_feed(self, url: str) -> list[NewsItem]:
        feed = feedparser.parse(url)
        items: list[NewsItem] = []
        for entry in feed.entries[: self.max_items]:
            summary = entry.get("summary", "") or entry.get("description", "")
            summary = BeautifulSoup(summary, "lxml").get_text(" ", strip=True)
            items.append(
                NewsItem(
                    title=entry.get("title", ""),
                    summary=summary[:600],
                    url=entry.get("link", ""),
                    source=feed.feed.get("title", url),
                    published=entry.get("published", ""),
                )
            )
        return items

    @staticmethod
    def _is_relevant(item: NewsItem) -> bool:
        text = (item.title + " " + item.summary).lower()
        return any(kw in text for kw in FIFA_KEYWORDS)

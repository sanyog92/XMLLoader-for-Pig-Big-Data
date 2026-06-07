"""
Google Trends wrapper — surfaces the most viral FIFA 2026 search terms
so the bot can bias its content towards what's trending right now.
"""

from __future__ import annotations

from pytrends.request import TrendReq
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import logger

_SEED_KEYWORDS = [
    "FIFA World Cup 2026",
    "World Cup 2026 goals",
    "World Cup 2026 highlights",
    "World Cup 2026 match",
]


class TrendsCrawler:
    def __init__(self, geo: str = "", timeframe: str = "now 1-d"):
        self.pytrends = TrendReq(hl="en-US", tz=0)
        self.geo = geo
        self.timeframe = timeframe

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30))
    def get_trending_keywords(self) -> list[str]:
        """Return a ranked list of currently trending FIFA-related search terms."""
        try:
            self.pytrends.build_payload(
                _SEED_KEYWORDS[:4],
                cat=20,  # Sports category
                timeframe=self.timeframe,
                geo=self.geo,
            )
            related = self.pytrends.related_queries()
            keywords: list[str] = []
            for seed in _SEED_KEYWORDS[:4]:
                top_df = (related.get(seed) or {}).get("top")
                if top_df is not None and not top_df.empty:
                    keywords.extend(top_df["query"].tolist()[:5])
            logger.info(f"Trending keywords discovered: {keywords[:10]}")
            return keywords[:20]
        except Exception as exc:
            logger.warning(f"Trends API failed: {exc}")
            return _SEED_KEYWORDS

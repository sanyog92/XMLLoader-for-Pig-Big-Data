"""
AI-powered caption and title generator.

Uses OpenAI GPT-4o (primary) or Claude (fallback) to craft:
  - Short YouTube title (max 80 chars)
  - YouTube description (SEO-optimised, ~300 words)
  - Instagram caption (≤2200 chars with hashtags)
"""

from __future__ import annotations

from typing import Optional

from config.settings import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    ENABLE_AI_CAPTIONS,
    YT_SHORTS_HASHTAGS,
    IG_DEFAULT_CAPTION_SUFFIX,
)
from utils.logger import logger


_SYSTEM_PROMPT = (
    "You are a viral social-media editor specialising in FIFA World Cup 2026 content. "
    "Write punchy, engaging text that drives clicks, views and shares. "
    "Always include relevant emojis. Keep titles under 80 characters."
)


class CaptionGenerator:
    def generate(
        self,
        raw_title: str,
        description: str = "",
        tags: Optional[list[str]] = None,
    ) -> dict:
        """
        Returns:
          {
            "yt_title": str,
            "yt_description": str,
            "ig_caption": str,
          }
        """
        if not ENABLE_AI_CAPTIONS:
            return self._fallback(raw_title)

        try:
            return self._generate_openai(raw_title, description, tags or [])
        except Exception as exc:
            logger.warning(f"OpenAI caption failed: {exc}, trying Anthropic...")
        try:
            return self._generate_anthropic(raw_title, description, tags or [])
        except Exception as exc:
            logger.warning(f"Anthropic caption also failed: {exc}, using fallback.")
        return self._fallback(raw_title)

    # ── OpenAI ────────────────────────────────────────────────

    def _generate_openai(self, title: str, desc: str, tags: list[str]) -> dict:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        prompt = self._build_prompt(title, desc, tags)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.9,
        )
        return self._parse_response(resp.choices[0].message.content, title)

    # ── Anthropic ─────────────────────────────────────────────

    def _generate_anthropic(self, title: str, desc: str, tags: list[str]) -> dict:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = self._build_prompt(title, desc, tags)
        resp = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=800,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_response(resp.content[0].text, title)

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _build_prompt(title: str, desc: str, tags: list[str]) -> str:
        return (
            f"Original video title: {title}\n"
            f"Description snippet: {desc[:300]}\n"
            f"Tags: {', '.join(tags[:10])}\n\n"
            "Return a JSON object with exactly these keys:\n"
            "  yt_title      – punchy YouTube Short title (≤80 chars, include emojis)\n"
            "  yt_description – SEO YouTube description (200-350 words)\n"
            "  ig_caption    – Instagram Reel caption (≤300 chars + hashtags)\n"
        )

    @staticmethod
    def _parse_response(raw: str, fallback_title: str) -> dict:
        import json, re
        try:
            # Extract JSON block if wrapped in markdown
            match = re.search(r"\{[\s\S]+\}", raw)
            data = json.loads(match.group() if match else raw)
            return {
                "yt_title": str(data.get("yt_title", fallback_title))[:100],
                "yt_description": str(data.get("yt_description", ""))[:5000],
                "ig_caption": str(data.get("ig_caption", fallback_title))[:2200],
            }
        except Exception:
            return CaptionGenerator._fallback(fallback_title)

    @staticmethod
    def _fallback(title: str) -> dict:
        short_title = f"⚽ {title[:70]} | FIFA World Cup 2026 #Shorts"
        return {
            "yt_title": short_title[:100],
            "yt_description": (
                f"{title}\n\nFIFA World Cup 2026 Highlights — Best moments, goals, "
                f"and viral clips from the tournament.\n\n{YT_SHORTS_HASHTAGS}"
            ),
            "ig_caption": f"⚽ {title[:200]}{IG_DEFAULT_CAPTION_SUFFIX}",
        }

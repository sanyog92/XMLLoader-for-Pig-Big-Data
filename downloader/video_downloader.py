"""
Downloads source videos via yt-dlp.
Returns local file paths ready for the editor.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import yt_dlp
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import DOWNLOAD_DIR, MAX_SOURCE_DURATION
from utils.logger import logger
from utils.helpers import slugify, sha256_id


class VideoDownloader:
    """Downloads videos to DOWNLOAD_DIR using yt-dlp."""

    _FORMAT = (
        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"
        "/bestvideo[height<=1080]+bestaudio"
        "/best[height<=1080][ext=mp4]"
        "/best"
    )

    def __init__(self, output_dir: Path = DOWNLOAD_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, title: str = "") -> Optional[Path]:
        """Download a video and return its local path, or None on failure."""
        safe_name = slugify(title) if title else sha256_id(url)
        out_tmpl = str(self.output_dir / f"{safe_name}.%(ext)s")

        opts = {
            "format": self._FORMAT,
            "outtmpl": out_tmpl,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
            "match_filter": yt_dlp.utils.match_filter_func(
                f"duration <= {MAX_SOURCE_DURATION}"
            ),
        }

        try:
            return self._run_download(url, opts, safe_name)
        except Exception as exc:
            logger.error(f"Download failed for {url}: {exc}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=3, max=30))
    def _run_download(self, url: str, opts: dict, safe_name: str) -> Optional[Path]:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Resolve actual output file
        if info:
            ext = info.get("ext", "mp4")
            candidate = self.output_dir / f"{safe_name}.{ext}"
            if candidate.exists():
                logger.info(f"Downloaded: {candidate.name} ({candidate.stat().st_size // 1024} KB)")
                return candidate

        # Fallback: find any mp4 matching our slug
        matches = sorted(self.output_dir.glob(f"{safe_name}*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            logger.info(f"Downloaded (glob): {matches[0].name}")
            return matches[0]

        return None

    def get_info(self, url: str) -> dict:
        """Fetch metadata only (no download)."""
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False) or {}
        except Exception as exc:
            logger.warning(f"get_info failed for {url}: {exc}")
            return {}

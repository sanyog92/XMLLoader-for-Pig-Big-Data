"""
Core pipeline — ties all modules together.

Flow per run:
  1. Discover trending FIFA 2026 videos (YouTube crawler)
  2. Fetch trending keywords (Google Trends)
  3. Download top-N candidate videos
  4. For each downloaded video:
       a. Generate AI title / caption
       b. Edit into portrait Short/Reel
       c. Generate thumbnail
       d. Upload to YouTube Shorts
       e. Upload to Instagram Reels
  5. Record processed IDs to avoid re-processing
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from config.settings import (
    MAX_SHORTS_PER_RUN,
    ENABLE_YOUTUBE_UPLOAD,
    ENABLE_INSTAGRAM_UPLOAD,
    DOWNLOAD_DIR,
    EDITED_DIR,
    THUMBNAIL_DIR,
)
from crawler.youtube_crawler import YouTubeCrawler, VideoMeta
from crawler.trends import TrendsCrawler
from downloader.video_downloader import VideoDownloader
from editor.video_editor import VideoEditor
from editor.thumbnail_gen import ThumbnailGenerator
from editor.music_manager import MusicManager
from uploader.caption_generator import CaptionGenerator
from uploader.youtube_uploader import YouTubeUploader
from uploader.instagram_uploader import InstagramUploader
from utils.logger import logger
from utils.helpers import sha256_id

_PROCESSED_LOG = Path("output/processed_ids.json")


class Pipeline:
    def __init__(self):
        self.yt_crawler = YouTubeCrawler()
        self.trends = TrendsCrawler()
        self.downloader = VideoDownloader()
        self.editor = VideoEditor()
        self.thumb_gen = ThumbnailGenerator()
        self.music_mgr = MusicManager()
        self.caption_gen = CaptionGenerator()
        self.yt_uploader = YouTubeUploader() if ENABLE_YOUTUBE_UPLOAD else None
        self.ig_uploader = InstagramUploader() if ENABLE_INSTAGRAM_UPLOAD else None
        self._processed: set[str] = self._load_processed()

    # ── Main entry point ──────────────────────────────────────

    def run(self) -> None:
        logger.info("=" * 60)
        logger.info("Pipeline run started")

        # 1. Discover
        candidates = self.yt_crawler.discover()
        logger.info(f"Discovered {len(candidates)} candidates")

        # Filter already-processed
        fresh = [v for v in candidates if v.id not in self._processed]
        logger.info(f"Fresh (unprocessed) candidates: {len(fresh)}")

        if not fresh:
            logger.info("Nothing new to process.")
            return

        # 2. Process top-N
        produced = 0
        for video in fresh[:MAX_SHORTS_PER_RUN * 3]:  # extra buffer for failures
            if produced >= MAX_SHORTS_PER_RUN:
                break
            success = self._process_one(video)
            if success:
                produced += 1
            self._mark_processed(video.id)

        logger.info(f"Pipeline run complete. Produced {produced} short(s).")

    # ── Per-video pipeline ────────────────────────────────────

    def _process_one(self, video: VideoMeta) -> bool:
        logger.info(f"Processing: {video.title[:60]}")

        # Download
        video_path = self.downloader.download(video.url, video.title)
        if not video_path:
            logger.warning(f"Download failed, skipping: {video.url}")
            return False

        # AI captions
        captions = self.caption_gen.generate(
            raw_title=video.title,
            description=video.description,
            tags=video.tags,
        )
        yt_title = captions["yt_title"]
        yt_desc = captions["yt_description"]
        ig_caption = captions["ig_caption"]

        # Music
        music = self.music_mgr.get_track(mood="hype")

        # Edit video
        edited_path = self.editor.edit(
            input_path=video_path,
            title=yt_title,
            hashtags="#Shorts #FIFA2026 #WorldCup2026",
            music_path=music,
        )
        if not edited_path:
            logger.warning("Edit failed, skipping upload.")
            return False

        # Generate thumbnail
        thumb_path = self.thumb_gen.generate(
            video_path=edited_path,
            title=yt_title,
            subtitle="FIFA World Cup 2026",
            frame_sec=2.0,
        )

        # Upload to YouTube
        if ENABLE_YOUTUBE_UPLOAD and self.yt_uploader:
            yt_id = self.yt_uploader.upload(
                video_path=edited_path,
                title=yt_title,
                description=yt_desc,
                thumbnail_path=thumb_path,
                tags=video.tags,
            )
            if yt_id:
                logger.info(f"YouTube Short live: https://www.youtube.com/shorts/{yt_id}")

        # Upload to Instagram
        if ENABLE_INSTAGRAM_UPLOAD and self.ig_uploader:
            cover_url = None  # Set if you host thumbnails publicly
            ig_id = self.ig_uploader.upload_reel(
                video_path=edited_path,
                caption=ig_caption,
                cover_url=cover_url,
            )
            if ig_id:
                logger.info(f"Instagram Reel live: media_id={ig_id}")

        return True

    # ── Processed-IDs persistence ─────────────────────────────

    def _load_processed(self) -> set[str]:
        if _PROCESSED_LOG.exists():
            try:
                return set(json.loads(_PROCESSED_LOG.read_text()))
            except Exception:
                pass
        return set()

    def _mark_processed(self, vid_id: str) -> None:
        self._processed.add(vid_id)
        _PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
        _PROCESSED_LOG.write_text(json.dumps(list(self._processed)))

    # ── Cleanup ───────────────────────────────────────────────

    def cleanup_old_files(self, days: int = 3) -> None:
        """Delete downloaded / edited files older than `days` days."""
        import time as _time
        cutoff = _time.time() - days * 86400
        for folder in (DOWNLOAD_DIR, EDITED_DIR):
            for f in folder.iterdir():
                if f.is_file() and f.stat().st_mtime < cutoff:
                    f.unlink()
                    logger.debug(f"Deleted old file: {f.name}")

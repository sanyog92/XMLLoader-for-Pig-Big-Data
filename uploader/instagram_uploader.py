"""
Uploads finished Reels to Instagram via the Instagram Graph API.

Requirements:
  - Instagram Business or Creator account
  - Facebook Developer app with instagram_basic + instagram_content_publish permissions
  - A long-lived access token (rotate every ~60 days)
  - The video must be accessible at a public HTTPS URL during the upload window
    (use INSTAGRAM_MEDIA_HOST_URL in .env, or a local ngrok tunnel for testing)

Graph API flow:
  1. POST /me/media          → create container (returns creation_id)
  2. Poll /me/media/{id}     → wait until STATUS == FINISHED
  3. POST /me/media_publish  → publish the container
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests

from config.settings import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_BUSINESS_ACCOUNT_ID,
    INSTAGRAM_MEDIA_HOST_URL,
    IG_DEFAULT_CAPTION_SUFFIX,
    DRY_RUN,
)
from utils.logger import logger

_GRAPH_BASE = "https://graph.facebook.com/v19.0"
_MAX_POLL_ATTEMPTS = 20
_POLL_INTERVAL_SEC = 10


class InstagramUploader:
    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.account_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.host_url = INSTAGRAM_MEDIA_HOST_URL.rstrip("/") + "/"

    # ── Public API ────────────────────────────────────────────

    def upload_reel(
        self,
        video_path: Path,
        caption: str = "",
        cover_url: Optional[str] = None,
    ) -> Optional[str]:
        """Upload a Reel and return the Instagram media ID, or None on failure."""
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would upload to Instagram: {video_path.name}")
            return "dry_run_media_id"

        if not self.access_token or not self.account_id:
            logger.error("Instagram credentials not configured. Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID.")
            return None

        try:
            video_url = self._public_url(video_path)
            full_caption = (caption + IG_DEFAULT_CAPTION_SUFFIX)[:2200]

            logger.info(f"Creating Instagram Reel container for {video_path.name}...")
            container_id = self._create_container(video_url, full_caption, cover_url)
            if not container_id:
                return None

            logger.info("Waiting for container to finish processing...")
            if not self._wait_for_container(container_id):
                return None

            logger.info("Publishing Reel...")
            media_id = self._publish_container(container_id)
            if media_id:
                logger.info(f"Instagram Reel published: media_id={media_id}")
            return media_id
        except Exception as exc:
            logger.error(f"Instagram upload failed: {exc}")
            return None

    # ── Graph API helpers ─────────────────────────────────────

    def _create_container(
        self, video_url: str, caption: str, cover_url: Optional[str]
    ) -> Optional[str]:
        endpoint = f"{_GRAPH_BASE}/{self.account_id}/media"
        data = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": self.access_token,
        }
        if cover_url:
            data["cover_url"] = cover_url

        resp = requests.post(endpoint, data=data, timeout=60)
        if resp.ok:
            return resp.json().get("id")
        logger.error(f"Container creation failed: {resp.status_code} {resp.text}")
        return None

    def _wait_for_container(self, container_id: str) -> bool:
        endpoint = f"{_GRAPH_BASE}/{container_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token,
        }
        for attempt in range(_MAX_POLL_ATTEMPTS):
            resp = requests.get(endpoint, params=params, timeout=30)
            if not resp.ok:
                logger.warning(f"Poll attempt {attempt+1} failed: {resp.text}")
                time.sleep(_POLL_INTERVAL_SEC)
                continue

            data = resp.json()
            status = data.get("status_code", "")
            logger.debug(f"Container status: {status}")

            if status == "FINISHED":
                return True
            if status in ("ERROR", "EXPIRED"):
                logger.error(f"Container failed with status: {status} — {data.get('status')}")
                return False

            time.sleep(_POLL_INTERVAL_SEC)

        logger.error("Container processing timed out.")
        return False

    def _publish_container(self, container_id: str) -> Optional[str]:
        endpoint = f"{_GRAPH_BASE}/{self.account_id}/media_publish"
        data = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }
        resp = requests.post(endpoint, data=data, timeout=30)
        if resp.ok:
            return resp.json().get("id")
        logger.error(f"Publish failed: {resp.status_code} {resp.text}")
        return None

    def _public_url(self, video_path: Path) -> str:
        """Build the public URL for the local video file."""
        if not self.host_url or self.host_url == "/":
            raise RuntimeError(
                "INSTAGRAM_MEDIA_HOST_URL not set. "
                "The video must be accessible at a public HTTPS URL."
            )
        return urljoin(self.host_url, video_path.name)

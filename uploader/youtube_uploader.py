"""
Uploads finished shorts to YouTube via the YouTube Data API v3.

Auth flow:
  - First run: opens browser for OAuth2 consent → saves token.json
  - Subsequent runs: refreshes token automatically
"""

from __future__ import annotations

import json
import os
import pickle
import time
from pathlib import Path
from typing import Optional

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google.auth.transport.requests import Request

from config.settings import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REFRESH_TOKEN,
    YT_DEFAULT_CATEGORY_ID,
    YT_DEFAULT_PRIVACY,
    YT_SHORTS_HASHTAGS,
    DRY_RUN,
)
from utils.logger import logger

_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
_TOKEN_FILE = Path("config/youtube_token.pickle")
_CLIENT_SECRETS_FILE = Path("config/youtube_client_secrets.json")
_API_SERVICE = "youtube"
_API_VERSION = "v3"


class YouTubeUploader:
    def __init__(self):
        self._service = None

    # ── Public API ────────────────────────────────────────────

    def upload(
        self,
        video_path: Path,
        title: str,
        description: str = "",
        thumbnail_path: Optional[Path] = None,
        tags: Optional[list[str]] = None,
    ) -> Optional[str]:
        """Upload a short and return the YouTube video ID, or None on failure."""
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would upload to YouTube: {video_path.name}")
            return "dry_run_video_id"

        try:
            service = self._get_service()
            video_id = self._upload_video(service, video_path, title, description, tags)
            if video_id and thumbnail_path and thumbnail_path.exists():
                self._set_thumbnail(service, video_id, thumbnail_path)
            return video_id
        except Exception as exc:
            logger.error(f"YouTube upload failed: {exc}")
            return None

    # ── Upload helpers ────────────────────────────────────────

    def _upload_video(
        self,
        service,
        video_path: Path,
        title: str,
        description: str,
        tags: Optional[list[str]],
    ) -> Optional[str]:
        full_desc = f"{description}\n\n{YT_SHORTS_HASHTAGS}".strip()
        body = {
            "snippet": {
                "title": title[:100],
                "description": full_desc[:5000],
                "tags": (tags or []) + ["Shorts", "FIFA2026", "WorldCup2026", "Football"],
                "categoryId": YT_DEFAULT_CATEGORY_ID,
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": YT_DEFAULT_PRIVACY,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = googleapiclient.http.MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=5 * 1024 * 1024,  # 5 MB chunks
        )

        request = service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        video_id = None
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                logger.debug(f"YouTube upload progress: {pct}%")

        video_id = response.get("id")
        yt_url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info(f"Uploaded to YouTube: {yt_url}")
        return video_id

    def _set_thumbnail(self, service, video_id: str, thumbnail_path: Path) -> None:
        try:
            service.thumbnails().set(
                videoId=video_id,
                media_body=googleapiclient.http.MediaFileUpload(str(thumbnail_path)),
            ).execute()
            logger.info(f"Thumbnail set for video {video_id}")
        except Exception as exc:
            logger.warning(f"Thumbnail upload failed: {exc}")

    # ── Auth ──────────────────────────────────────────────────

    def _get_service(self):
        if self._service:
            return self._service
        creds = self._load_credentials()
        self._service = googleapiclient.discovery.build(
            _API_SERVICE, _API_VERSION, credentials=creds
        )
        return self._service

    def _load_credentials(self) -> google.oauth2.credentials.Credentials:
        # 1. Try saved token pickle
        if _TOKEN_FILE.exists():
            with open(_TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._save_token(creds)
                return creds

        # 2. Try env-var refresh token
        if YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN:
            creds = google.oauth2.credentials.Credentials(
                token=None,
                refresh_token=YOUTUBE_REFRESH_TOKEN,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=YOUTUBE_CLIENT_ID,
                client_secret=YOUTUBE_CLIENT_SECRET,
                scopes=_SCOPES,
            )
            creds.refresh(Request())
            self._save_token(creds)
            return creds

        # 3. Interactive OAuth flow (first-time setup)
        if _CLIENT_SECRETS_FILE.exists():
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(_CLIENT_SECRETS_FILE), _SCOPES
            )
            creds = flow.run_local_server(port=0)
            self._save_token(creds)
            return creds

        raise RuntimeError(
            "No YouTube credentials found. Set YOUTUBE_CLIENT_ID, "
            "YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN in .env "
            "or place config/youtube_client_secrets.json."
        )

    @staticmethod
    def _save_token(creds) -> None:
        _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

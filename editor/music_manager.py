"""
Manages the royalty-free music library used for background tracks.

Provides:
 - Listing available tracks
 - Picking tracks by mood / BPM
 - Downloading free tracks from Pixabay / ccMixter if library is empty
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import MUSIC_DIR
from utils.logger import logger

# Free, royalty-free music sources (no API key required)
_FREE_TRACK_URLS = [
    # Pixabay free music (direct mp3 links — verify & replace with current ones)
    "https://cdn.pixabay.com/audio/2023/03/07/audio_4d047d9947.mp3",
    "https://cdn.pixabay.com/audio/2022/10/30/audio_e89f8e3ee5.mp3",
    "https://cdn.pixabay.com/audio/2023/04/28/audio_f6c8b39e3f.mp3",
]

MOOD_TAGS = {
    "hype": ["energetic", "epic", "stadium", "crowd"],
    "dramatic": ["tension", "cinematic", "orchestral"],
    "chill": ["ambient", "lo-fi", "calm"],
}


class MusicManager:
    def __init__(self, music_dir: Path = MUSIC_DIR):
        self.music_dir = music_dir
        self.music_dir.mkdir(parents=True, exist_ok=True)

    def get_track(self, mood: str = "hype") -> Optional[Path]:
        """Return a suitable track for the given mood."""
        tracks = self._list_tracks()
        if not tracks:
            logger.info("Music library empty, attempting download of free tracks...")
            self._download_free_tracks()
            tracks = self._list_tracks()
        if not tracks:
            logger.warning("No music tracks available.")
            return None
        # Naive mood selection: shuffle and pick first
        random.shuffle(tracks)
        return tracks[0]

    def _list_tracks(self) -> list[Path]:
        return (
            list(self.music_dir.glob("*.mp3"))
            + list(self.music_dir.glob("*.m4a"))
            + list(self.music_dir.glob("*.wav"))
        )

    def _download_free_tracks(self) -> None:
        for i, url in enumerate(_FREE_TRACK_URLS):
            dest = self.music_dir / f"track_{i+1:02d}.mp3"
            if dest.exists():
                continue
            try:
                self._download_file(url, dest)
                logger.info(f"Downloaded music track: {dest.name}")
            except Exception as exc:
                logger.warning(f"Could not download track from {url}: {exc}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20))
    def _download_file(self, url: str, dest: Path) -> None:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)

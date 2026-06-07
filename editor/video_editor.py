"""
Transforms raw downloaded clips into portrait-format Shorts / Reels.

Pipeline per clip:
  1. Trim to SHORT_DURATION seconds (taking the most action-dense segment)
  2. Crop / pad to 9:16 portrait (1080×1920)
  3. Add animated text overlay (title + hashtags)
  4. Mix in background music at low volume
  5. Export to output/edited/
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Optional

import numpy as np
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    CompositeAudioClip,
    concatenate_videoclips,
    ColorClip,
)
from moviepy.video.fx.all import crop, resize
from PIL import Image

from config.settings import (
    SHORT_DURATION,
    OUTPUT_WIDTH,
    OUTPUT_HEIGHT,
    MUSIC_DIR,
    MUSIC_VOLUME,
    EDITED_DIR,
)
from utils.logger import logger
from utils.helpers import slugify, timestamp_str


class VideoEditor:
    """Edits a raw video into a Short/Reel ready for upload."""

    TARGET_W = OUTPUT_WIDTH    # 1080
    TARGET_H = OUTPUT_HEIGHT   # 1920
    ASPECT = TARGET_W / TARGET_H  # 9:16

    def __init__(self, output_dir: Path = EDITED_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Public ────────────────────────────────────────────────

    def edit(
        self,
        input_path: Path,
        title: str = "",
        hashtags: str = "#Shorts #FIFA2026 #WorldCup2026",
        music_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """Full editing pipeline. Returns path to finished short or None."""
        try:
            return self._pipeline(input_path, title, hashtags, music_path)
        except Exception as exc:
            logger.error(f"Edit failed for {input_path.name}: {exc}")
            return None

    # ── Pipeline steps ────────────────────────────────────────

    def _pipeline(
        self,
        input_path: Path,
        title: str,
        hashtags: str,
        music_path: Optional[Path],
    ) -> Path:
        logger.info(f"Editing: {input_path.name}")
        clip = VideoFileClip(str(input_path))

        # 1. Trim
        clip = self._smart_trim(clip)

        # 2. Portrait crop
        clip = self._to_portrait(clip)

        # 3. Text overlays
        composite = self._add_overlays(clip, title, hashtags)

        # 4. Music
        if music_path is None:
            music_path = self._pick_random_music()
        if music_path:
            composite = self._mix_music(composite, music_path)

        # 5. Export
        out_name = f"{slugify(title) or 'short'}_{timestamp_str()}.mp4"
        out_path = self.output_dir / out_name
        composite.write_videofile(
            str(out_path),
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="fast",
            threads=4,
            logger=None,
        )
        composite.close()
        clip.close()
        logger.info(f"Exported short: {out_path.name}")
        return out_path

    # ── Step helpers ──────────────────────────────────────────

    def _smart_trim(self, clip: VideoFileClip) -> VideoFileClip:
        """Trim to SHORT_DURATION; favour the most 'action' part via motion heuristic."""
        duration = clip.duration
        target = min(float(SHORT_DURATION), duration)

        if duration <= target:
            return clip

        # Simple heuristic: start 10 % in to skip intros
        max_start = duration - target
        start = min(duration * 0.1, max_start)
        return clip.subclip(start, start + target)

    def _to_portrait(self, clip: VideoFileClip) -> VideoFileClip:
        """Crop/pad clip to 9:16 (1080×1920)."""
        w, h = clip.w, clip.h
        src_aspect = w / h

        if abs(src_aspect - self.ASPECT) < 0.01:
            return clip.resize((self.TARGET_W, self.TARGET_H))

        if src_aspect > self.ASPECT:
            # Wider than target → crop sides
            new_w = int(h * self.ASPECT)
            clipped = crop(clip, width=new_w, height=h, x_center=w / 2, y_center=h / 2)
        else:
            # Taller or square → crop top/bottom
            new_h = int(w / self.ASPECT)
            clipped = crop(clip, width=w, height=new_h, x_center=w / 2, y_center=h / 2)

        return clipped.resize((self.TARGET_W, self.TARGET_H))

    def _add_overlays(
        self, clip: VideoFileClip, title: str, hashtags: str
    ) -> CompositeVideoClip:
        layers = [clip]

        if title:
            # Semi-transparent dark bar at bottom
            bar_h = 180
            bar = (
                ColorClip(size=(self.TARGET_W, bar_h), color=(0, 0, 0))
                .set_opacity(0.55)
                .set_duration(clip.duration)
                .set_position(("center", self.TARGET_H - bar_h))
            )
            layers.append(bar)

            # Title text
            try:
                title_clip = (
                    TextClip(
                        title[:60],
                        fontsize=52,
                        color="white",
                        font="DejaVu-Sans-Bold",
                        size=(self.TARGET_W - 60, None),
                        method="caption",
                        align="center",
                    )
                    .set_duration(clip.duration)
                    .set_position(("center", self.TARGET_H - bar_h + 20))
                )
                layers.append(title_clip)

                hashtag_clip = (
                    TextClip(
                        hashtags,
                        fontsize=32,
                        color="#FFD700",
                        font="DejaVu-Sans",
                        size=(self.TARGET_W - 60, None),
                        method="caption",
                        align="center",
                    )
                    .set_duration(clip.duration)
                    .set_position(("center", self.TARGET_H - 60))
                )
                layers.append(hashtag_clip)
            except Exception as exc:
                logger.warning(f"TextClip failed (ImageMagick missing?): {exc}")

        return CompositeVideoClip(layers, size=(self.TARGET_W, self.TARGET_H))

    def _mix_music(
        self, clip: CompositeVideoClip, music_path: Path
    ) -> CompositeVideoClip:
        try:
            music = AudioFileClip(str(music_path)).volumex(MUSIC_VOLUME)
            if music.duration < clip.duration:
                # Loop music if shorter than clip
                loops = int(clip.duration / music.duration) + 1
                from moviepy.editor import concatenate_audioclips
                music = concatenate_audioclips([music] * loops)
            music = music.subclip(0, clip.duration)

            original_audio = clip.audio
            if original_audio:
                mixed = CompositeAudioClip([original_audio, music])
                return clip.set_audio(mixed)
            else:
                return clip.set_audio(music)
        except Exception as exc:
            logger.warning(f"Music mixing failed: {exc}")
            return clip

    def _pick_random_music(self) -> Optional[Path]:
        if not MUSIC_DIR.exists():
            return None
        tracks = list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.m4a"))
        return random.choice(tracks) if tracks else None

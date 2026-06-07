"""
Generates eye-catching thumbnails for YouTube uploads.

Layout:
 - Full-bleed frame extracted from the video
 - Dark gradient overlay at bottom
 - Bold white title text
 - FIFA 2026 branding badge (top-right)
 - Optional team flags / score badge
"""

from __future__ import annotations

import io
import os
import textwrap
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from config.settings import (
    THUMBNAIL_WIDTH,
    THUMBNAIL_HEIGHT,
    THUMBNAIL_DIR,
    FONT_DIR,
)
from utils.logger import logger
from utils.helpers import slugify, timestamp_str


class ThumbnailGenerator:
    W = THUMBNAIL_WIDTH   # 1280
    H = THUMBNAIL_HEIGHT  # 720

    def __init__(self, output_dir: Path = THUMBNAIL_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._title_font = self._load_font(80)
        self._sub_font = self._load_font(42)
        self._badge_font = self._load_font(28)

    # ── Public ────────────────────────────────────────────────

    def generate(
        self,
        video_path: Path,
        title: str,
        subtitle: str = "FIFA World Cup 2026",
        frame_sec: float = 3.0,
    ) -> Optional[Path]:
        try:
            return self._build(video_path, title, subtitle, frame_sec)
        except Exception as exc:
            logger.error(f"Thumbnail generation failed: {exc}")
            return None

    # ── Build pipeline ────────────────────────────────────────

    def _build(
        self,
        video_path: Path,
        title: str,
        subtitle: str,
        frame_sec: float,
    ) -> Path:
        # 1. Extract frame
        frame = self._extract_frame(video_path, frame_sec)

        # 2. Resize / crop to thumbnail dimensions
        frame = self._fit_crop(frame, self.W, self.H)

        # 3. Enhance
        frame = ImageEnhance.Brightness(frame).enhance(1.05)
        frame = ImageEnhance.Contrast(frame).enhance(1.1)
        frame = ImageEnhance.Sharpness(frame).enhance(1.3)

        canvas = frame.copy()
        draw = ImageDraw.Draw(canvas)

        # 4. Bottom gradient overlay
        self._draw_gradient(canvas)

        # 5. Title text
        self._draw_title(draw, title)

        # 6. Subtitle / branding
        self._draw_subtitle(draw, subtitle)

        # 7. FIFA badge
        self._draw_badge(draw)

        # 8. Save
        out_name = f"{slugify(title) or 'thumb'}_{timestamp_str()}.jpg"
        out_path = self.output_dir / out_name
        canvas.save(str(out_path), "JPEG", quality=95)
        logger.info(f"Thumbnail saved: {out_path.name}")
        return out_path

    # ── Step helpers ──────────────────────────────────────────

    def _extract_frame(self, video_path: Path, frame_sec: float) -> Image.Image:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        target_frame = min(int(frame_sec * fps), total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return Image.new("RGB", (self.W, self.H), (20, 20, 40))
        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    @staticmethod
    def _fit_crop(img: Image.Image, w: int, h: int) -> Image.Image:
        src_w, src_h = img.size
        scale = max(w / src_w, h / src_h)
        new_w, new_h = int(src_w * scale), int(src_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        return img.crop((left, top, left + w, top + h))

    @staticmethod
    def _draw_gradient(canvas: Image.Image) -> None:
        grad = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(grad)
        gradient_h = int(canvas.height * 0.55)
        for i in range(gradient_h):
            alpha = int(210 * (i / gradient_h))
            y = canvas.height - gradient_h + i
            draw.line([(0, y), (canvas.width, y)], fill=(0, 0, 0, alpha))
        canvas.paste(Image.fromarray(np.array(grad)[..., :3]), mask=grad)

    def _draw_title(self, draw: ImageDraw.Draw, title: str) -> None:
        lines = textwrap.wrap(title, width=28)[:3]
        y = self.H - 60 - len(lines) * 90
        for line in lines:
            # Shadow
            draw.text((42, y + 3), line, font=self._title_font, fill=(0, 0, 0, 200))
            draw.text((40, y), line, font=self._title_font, fill="white")
            y += 88

    def _draw_subtitle(self, draw: ImageDraw.Draw, subtitle: str) -> None:
        draw.text((42, self.H - 52), subtitle, font=self._sub_font, fill="#FFD700")

    def _draw_badge(self, draw: ImageDraw.Draw) -> None:
        badge_text = "⚽ FIFA 2026"
        bbox = draw.textbbox((0, 0), badge_text, font=self._badge_font)
        bw = bbox[2] - bbox[0] + 24
        bh = bbox[3] - bbox[1] + 14
        x1, y1 = self.W - bw - 20, 20
        x2, y2 = self.W - 20, 20 + bh
        draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill=(0, 90, 200, 230))
        draw.text((x1 + 12, y1 + 7), badge_text, font=self._badge_font, fill="white")

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        candidates = [
            FONT_DIR / "DejaVuSans-Bold.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
        ]
        for path in candidates:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        return ImageFont.load_default()

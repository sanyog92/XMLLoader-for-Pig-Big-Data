"""Shared utility helpers."""

import re
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime


def slugify(text: str) -> str:
    """Convert free-form text to a safe filename slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)[:80]


def sha256_id(text: str) -> str:
    """Short 12-char content fingerprint used for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def timestamp_str() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

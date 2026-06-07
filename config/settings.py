"""Central configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── YouTube ──────────────────────────────────────────────────
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# ── Instagram ────────────────────────────────────────────────
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
INSTAGRAM_MEDIA_HOST_URL = os.getenv("INSTAGRAM_MEDIA_HOST_URL", "")

# ── AI ────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Content sources ──────────────────────────────────────────
_raw_yt_channels = os.getenv(
    "YOUTUBE_SOURCE_CHANNELS",
    "UCpcTrCXblq78GZrTUTLWeBw,UC8-cU4aHHADFtCmSHQKMh0g",
)
YOUTUBE_SOURCE_CHANNELS = [c.strip() for c in _raw_yt_channels.split(",") if c.strip()]

_raw_ig_tags = os.getenv("INSTAGRAM_HASHTAGS", "FIFA2026,WorldCup2026,WorldCup")
INSTAGRAM_HASHTAGS = [t.strip() for t in _raw_ig_tags.split(",") if t.strip()]

FIFA_SEARCH_KEYWORDS = [
    "FIFA 2026 World Cup",
    "World Cup 2026 highlights",
    "World Cup 2026 goals",
    "World Cup 2026 best moments",
    "Copa Mundial 2026",
    "FIFA World Cup goal",
    "World Cup 2026 viral",
]

# ── Scheduler ────────────────────────────────────────────────
CRAWL_INTERVAL_MINUTES = int(os.getenv("CRAWL_INTERVAL_MINUTES", "30"))
MAX_SHORTS_PER_RUN = int(os.getenv("MAX_SHORTS_PER_RUN", "3"))
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# ── Video settings ───────────────────────────────────────────
MAX_SOURCE_DURATION = int(os.getenv("MAX_SOURCE_DURATION", "300"))
SHORT_DURATION = int(os.getenv("SHORT_DURATION", "58"))
OUTPUT_WIDTH = int(os.getenv("OUTPUT_WIDTH", "1080"))
OUTPUT_HEIGHT = int(os.getenv("OUTPUT_HEIGHT", "1920"))

# ── Music ─────────────────────────────────────────────────────
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.15"))
MUSIC_DIR = BASE_DIR / os.getenv("MUSIC_DIR", "assets/music")

# ── Paths ─────────────────────────────────────────────────────
DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "output/downloads")
EDITED_DIR = BASE_DIR / os.getenv("EDITED_DIR", "output/edited")
THUMBNAIL_DIR = BASE_DIR / os.getenv("THUMBNAIL_DIR", "output/thumbnails")
LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")

for _p in (DOWNLOAD_DIR, EDITED_DIR, THUMBNAIL_DIR, LOG_DIR):
    _p.mkdir(parents=True, exist_ok=True)

# ── Feature flags ────────────────────────────────────────────
ENABLE_YOUTUBE_UPLOAD = os.getenv("ENABLE_YOUTUBE_UPLOAD", "true").lower() == "true"
ENABLE_INSTAGRAM_UPLOAD = os.getenv("ENABLE_INSTAGRAM_UPLOAD", "true").lower() == "true"
ENABLE_AI_CAPTIONS = os.getenv("ENABLE_AI_CAPTIONS", "true").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# ── Thumbnail design ─────────────────────────────────────────
THUMBNAIL_WIDTH = 1280
THUMBNAIL_HEIGHT = 720
FONT_DIR = BASE_DIR / "assets" / "fonts"

# ── YouTube upload metadata defaults ────────────────────────
YT_DEFAULT_CATEGORY_ID = "17"   # Sports
YT_DEFAULT_PRIVACY = "public"
YT_SHORTS_HASHTAGS = "#Shorts #FIFA2026 #WorldCup2026 #Football"

# ── Instagram upload defaults ────────────────────────────────
IG_DEFAULT_CAPTION_SUFFIX = (
    "\n\n#FIFA2026 #WorldCup2026 #Football #Soccer #Reels "
    "#WorldCup #FIFAWorldCup #Goals #Highlights"
)

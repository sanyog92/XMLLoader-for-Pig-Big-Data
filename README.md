# ⚽ FIFA 2026 Shorts Bot

Fully-automated pipeline that discovers viral FIFA World Cup 2026 content, edits it into YouTube Shorts & Instagram Reels, generates AI-powered titles/captions/thumbnails, and posts to your accounts — all on a schedule.

---

## Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │              Scheduler (APScheduler)          │
                        │          runs every N minutes (default 30)    │
                        └────────────────────┬────────────────────────-─┘
                                             │
                        ┌────────────────────▼─────────────────────────┐
                        │                  PIPELINE                     │
                        │                                               │
   ┌───────────────┐    │  1. Crawl        YouTube search + channels   │
   │ Google Trends │───▶│  2. Download     yt-dlp (best quality MP4)   │
   └───────────────┘    │  3. Edit         MoviePy → 1080×1920 Short   │
                        │  4. Thumbnail    Pillow → 1280×720 JPEG      │
   ┌───────────────┐    │  5. AI Caption   OpenAI GPT-4o / Claude      │
   │  News RSS     │───▶│  6. Upload YT    YouTube Data API v3         │
   └───────────────┘    │  7. Upload IG    Instagram Graph API         │
                        └───────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Clone & install

```bash
git clone <repo-url>
cd XMLLoader-for-Pig-Big-Data
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Then edit .env with your API keys (see Credentials section below)
```

### 3. Test without uploading

```bash
python main.py --crawl-only        # Preview discovered videos
python main.py --once --dry-run    # Full pipeline, no uploads
```

### 4. Go live — run once

```bash
python main.py --once
```

### 5. Run continuously (daemon mode)

```bash
python main.py                     # Runs every 30 min by default
# Or with nohup for background:
nohup python main.py > logs/nohup.log 2>&1 &
```

---

## Credentials Setup

### YouTube (Data API v3)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → enable **YouTube Data API v3**
3. Create **OAuth 2.0 Client ID** (Desktop app)
4. Download `client_secrets.json` → save as `config/youtube_client_secrets.json`
5. Run `python main.py --once` — a browser tab opens for one-time consent
6. The token is saved to `config/youtube_token.pickle` for future runs

**OR** generate a refresh token manually and set these in `.env`:
```
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...
```

### Instagram (Graph API)

Instagram requires a **Business or Creator account** connected to a Facebook Page.

1. Create a [Facebook Developer App](https://developers.facebook.com/apps/)
2. Add the **Instagram Graph API** product
3. Get permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
4. Generate a **long-lived user access token** (valid 60 days — rotate regularly)
5. Find your **Instagram Business Account ID** via:
   ```
   GET https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_TOKEN
   ```
6. Set in `.env`:
   ```
   INSTAGRAM_ACCESS_TOKEN=...
   INSTAGRAM_BUSINESS_ACCOUNT_ID=...
   INSTAGRAM_MEDIA_HOST_URL=https://your-public-server.com/videos/
   ```

> **Important:** Instagram requires your video to be at a **public HTTPS URL** during upload.
> For local testing, use [ngrok](https://ngrok.com): `ngrok http 8080` and serve `output/edited/` on port 8080.

### OpenAI (AI Captions — optional)

```
OPENAI_API_KEY=sk-...
```

Falls back to Claude (Anthropic) if OpenAI fails, and then to template-based captions.

---

## Configuration Reference (`.env`)

| Variable | Default | Description |
|---|---|---|
| `CRAWL_INTERVAL_MINUTES` | `30` | How often to check for new content |
| `MAX_SHORTS_PER_RUN` | `3` | Max shorts produced per crawl |
| `SHORT_DURATION` | `58` | Target clip length in seconds |
| `OUTPUT_WIDTH` / `OUTPUT_HEIGHT` | `1080` / `1920` | Portrait short resolution |
| `MUSIC_VOLUME` | `0.15` | Background music volume (0–1) |
| `ENABLE_YOUTUBE_UPLOAD` | `true` | Toggle YouTube uploads |
| `ENABLE_INSTAGRAM_UPLOAD` | `true` | Toggle Instagram uploads |
| `ENABLE_AI_CAPTIONS` | `true` | Use GPT-4o for titles/captions |
| `DRY_RUN` | `false` | Skip all uploads (test mode) |
| `TIMEZONE` | `UTC` | Scheduler timezone |

---

## Adding Background Music

Drop royalty-free `.mp3` files into `assets/music/`. The bot picks one at random per video.

Free sources:
- [Pixabay Music](https://pixabay.com/music/) (no attribution required)
- [ccMixter](http://ccmixter.org/)
- [Free Music Archive](https://freemusicarchive.org/)

The `MusicManager` will attempt to auto-download a few starter tracks on first run if the folder is empty.

---

## File Structure

```
.
├── main.py                    # CLI entry point
├── pipeline.py                # Orchestrates all modules
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py            # All config loaded from .env
│   └── youtube_token.pickle   # Auto-generated after first OAuth
├── crawler/
│   ├── youtube_crawler.py     # YouTube search + channel scan
│   ├── news_crawler.py        # RSS news feeds
│   └── trends.py              # Google Trends integration
├── downloader/
│   └── video_downloader.py    # yt-dlp wrapper
├── editor/
│   ├── video_editor.py        # MoviePy edit pipeline
│   ├── thumbnail_gen.py       # Pillow thumbnail builder
│   └── music_manager.py       # Background music library
├── uploader/
│   ├── caption_generator.py   # OpenAI / Claude captions
│   ├── youtube_uploader.py    # YouTube Data API v3
│   └── instagram_uploader.py  # Instagram Graph API
├── scheduler/
│   └── job_scheduler.py       # APScheduler
├── utils/
│   ├── logger.py
│   └── helpers.py
├── assets/
│   ├── music/                 # Drop .mp3 files here
│   └── fonts/                 # Optional custom fonts
└── output/
    ├── downloads/             # Raw downloaded videos
    ├── edited/                # Finished shorts
    └── thumbnails/            # Generated thumbnails
```

---

## Running as a Service (Linux systemd)

```ini
# /etc/systemd/system/fifa-shorts-bot.service
[Unit]
Description=FIFA 2026 Shorts Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/XMLLoader-for-Pig-Big-Data
ExecStart=/path/to/.venv/bin/python main.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable fifa-shorts-bot
sudo systemctl start fifa-shorts-bot
sudo journalctl -fu fifa-shorts-bot
```

---

## Legal & Content Policy

- Only use this bot on content you have rights to republish (fair use highlights, official FIFA feeds, Creative Commons clips).
- Respect platform Terms of Service: YouTube ToS, Instagram ToS.
- Do not spam — keep `MAX_SHORTS_PER_RUN` reasonable (1–5 per run).
- AI-generated captions should be reviewed before fully autonomous posting.

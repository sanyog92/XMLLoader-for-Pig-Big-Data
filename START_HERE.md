# 🎯 START HERE — FIFA 2026 Shorts Bot

Your complete **fully-automated YouTube Shorts + Instagram Reels + ZEE5** pipeline is ready.

---

## 📁 What You Have

A production-ready bot that:

```
Every 30 minutes:
┌─────────────────────────────────────────────────┐
│ 1. Crawl FIFA Content                           │
│    • YouTube (search + channels)               │
│    • ZEE5 (India-focused sports)               │
│    • Google Trends (viral keywords)             │
│    • News RSS feeds                             │
├─────────────────────────────────────────────────┤
│ 2. Download Best Candidates                     │
│    • Best quality (1080p MP4)                  │
│    • Smart retry logic                          │
├─────────────────────────────────────────────────┤
│ 3. Transform into Shorts/Reels                  │
│    • Crop to 1080×1920 portrait                │
│    • Add animated title overlay                │
│    • Mix background music                       │
│    • ~58 seconds each                           │
├─────────────────────────────────────────────────┤
│ 4. Generate Thumbnails & Captions               │
│    • Eye-catching 1280×720 thumbnails          │
│    • AI-powered titles (GPT-4o / Claude)       │
│    • SEO-optimized descriptions                │
├─────────────────────────────────────────────────┤
│ 5. Auto-Post to Your Accounts                  │
│    • Upload to YouTube Shorts                  │
│    • Upload to Instagram Reels                 │
│    • Track uploads to prevent duplicates        │
└─────────────────────────────────────────────────┘
```

---

## ⚡ Getting Started (Pick Your Path)

### Path 1: Run Locally & Test (15 minutes)

```bash
# 1. Setup
bash setup.sh

# 2. Configure
cp .env.example .env
nano .env  # Add YouTube, Instagram, ZEE5 credentials

# 3. Test without uploading
python main.py --crawl-only          # See what it discovers
python main.py --once --dry-run      # Full pipeline, no uploads

# 4. If happy, upload for real
python main.py --once
```

**Then:** Run in background with `nohup python main.py > logs/bot.log 2>&1 &`

---

### Path 2: Deploy to Free Cloud (20 minutes) ✨ RECOMMENDED

**Choose ONE:**

#### Railway.app (Easiest)
```bash
# 1. Create account at railway.app (GitHub login)
# 2. Push to GitHub
git push origin main

# 3. In Railway: New Project → Deploy from GitHub
# 4. Add env variables (copy-paste from .env)
# 5. Done! Runs 24/7 free
```

#### Google Cloud Run (Cheapest Running)
```bash
gcloud run deploy fifa-shorts-bot \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars YOUTUBE_CLIENT_ID=... (etc)
```

#### AWS Lightsail ($3.50/mo)
- Free for 1 year
- Full Linux server
- See DEPLOYMENT_GUIDE.md for steps

---

### Path 3: Run as Linux Service (Best for VPS)

```bash
# 1. Copy service file
sudo cp fifa-shorts-bot.service /etc/systemd/system/

# 2. Edit the paths in the file
sudo nano /etc/systemd/system/fifa-shorts-bot.service

# 3. Enable & start
sudo systemctl daemon-reload
sudo systemctl enable fifa-shorts-bot
sudo systemctl start fifa-shorts-bot

# 4. Check status
sudo journalctl -fu fifa-shorts-bot
```

**Result:** Runs automatically at boot, restarts on failure ✅

---

## 🔐 Credentials (What You Need to Add)

### 1️⃣ YouTube (to upload Shorts)
- Create Google Cloud project
- Enable YouTube Data API v3
- Create OAuth 2.0 credentials
- Bot will auto-get refresh token first run
- Add to `.env`: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`

**How:** See `DEPLOYMENT_GUIDE.md` → **Option 1** → Section 1.4

### 2️⃣ Instagram (to upload Reels)
- Create Facebook Developer app
- Add Instagram Graph API
- Generate long-lived access token
- Find your Business Account ID
- Add to `.env`: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`

**Note:** You need a **public HTTPS URL** where edited videos are accessible. For local testing, use [ngrok](https://ngrok.com).

### 3️⃣ ZEE5 (to crawl Indian sports content)
- Create free ZEE5 account at [zee5.com](https://zee5.com)
- Add email & password to `.env`
- Bot auto-logs in and crawls FIFA 2026 content
- Add to `.env`: `ZEE5_EMAIL`, `ZEE5_PASSWORD`

### 4️⃣ OpenAI (optional, for AI titles)
- Get API key from [platform.openai.com](https://platform.openai.com)
- Add to `.env`: `OPENAI_API_KEY`
- Falls back to Claude (Anthropic) or templates if unavailable

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| **START_HERE.md** | This file — overview & quick navigation |
| **QUICKSTART_ZEE5.md** | Step-by-step setup (30 min) |
| **DEPLOYMENT_GUIDE.md** | Detailed platform comparison & setup |
| **README.md** | Architecture & configuration reference |
| **setup.sh** | Auto-installer for dependencies |

---

## 🎮 Commands You'll Use

```bash
# Preview content (no uploads)
python main.py --crawl-only

# Full pipeline, no uploads (test)
python main.py --once --dry-run

# Run once and upload
python main.py --once

# Run continuously (daemon)
python main.py
nohup python main.py > logs/bot.log 2>&1 &

# Check logs
tail -f logs/bot.log
ps aux | grep python
```

---

## 📊 What Gets Produced

Each run creates:

```
output/
├── downloads/
│   └── raw_video_name.mp4          # Downloaded source
├── edited/
│   └── short_20260614_120530.mp4   # Finished 1080×1920 Shorts
└── thumbnails/
    └── thumb_20260614_120530.jpg   # 1280×720 branded thumbnail

logs/
├── bot.log                          # Detailed logs
└── service.log                      # systemd logs (if running as service)

output/
└── processed_ids.json               # Prevents re-uploading same videos
```

---

## ✅ Checklist to Go Live

- [ ] Clone repo: `git clone ...`
- [ ] Run setup: `bash setup.sh`
- [ ] Create .env: `cp .env.example .env`
- [ ] Add YouTube credentials
- [ ] Add Instagram credentials
- [ ] Add ZEE5 credentials (email/password)
- [ ] Test locally: `python main.py --once --dry-run`
- [ ] Test upload: `python main.py --once`
- [ ] Deploy to cloud (Railway/Cloud Run) OR setup systemd
- [ ] Monitor logs: `tail -f logs/bot.log`
- [ ] Enjoy! 🎉

---

## 🚀 Quick Links

- **Set up in 30 min:** Read `QUICKSTART_ZEE5.md`
- **Deploy to cloud:** Read `DEPLOYMENT_GUIDE.md` → Choose platform
- **Full tech details:** Read `README.md`
- **Run as Linux service:** See `fifa-shorts-bot.service`
- **Docker deployment:** See `Dockerfile`
- **Railway quick deploy:** See `railway.json` & `Procfile`

---

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| "ModuleNotFoundError" | `pip install -r requirements.txt` |
| "ffmpeg not found" | `bash setup.sh` or `apt-get install ffmpeg` |
| "Auth failed" | Check credentials in `.env` |
| "No videos found" | Run `python main.py --crawl-only` to debug |
| "Upload fails" | Check logs: `tail -f logs/bot.log` |
| "Bot not running" | Check systemd: `sudo systemctl status fifa-shorts-bot` |

---

## 📞 Need Help?

1. Check **QUICKSTART_ZEE5.md** for step-by-step setup
2. Check **DEPLOYMENT_GUIDE.md** for platform-specific issues
3. Check logs: `tail -f logs/bot.log` or `sudo journalctl -fu fifa-shorts-bot`
4. Test locally: `python main.py --crawl-only` to verify connectivity

---

## 🎯 Next Steps (After Going Live)

1. **Monitor:** Check logs daily to see what's being posted
2. **Optimize:** Adjust `CRAWL_INTERVAL_MINUTES` & `MAX_SHORTS_PER_RUN`
3. **Add Music:** Drop royalty-free .mp3 files in `assets/music/`
4. **Tune Keywords:** Edit `FIFA_SEARCH_KEYWORDS` in `config/settings.py`
5. **Scale:** Consider dedicated server if volume exceeds cloud limits

---

## 🎉 You're Ready!

Your bot is now:
- ✅ Crawling **YouTube**, **ZEE5**, **Google Trends**, **News RSS**
- ✅ Downloading & editing into **1080×1920 Shorts**
- ✅ Generating **AI captions** & **branded thumbnails**
- ✅ Uploading to **YouTube Shorts** & **Instagram Reels**
- ✅ Running **24/7 automatically** in the background
- ✅ Deployed on **free/cheap cloud** if you chose

Start with **QUICKSTART_ZEE5.md** and you'll be live in 30 minutes. 🚀⚽

Good luck! 🎬✨

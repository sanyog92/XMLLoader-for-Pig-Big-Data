# 🔧 Troubleshooting & FAQ

Common issues and solutions.

---

## Installation & Setup

### "ModuleNotFoundError: No module named 'moviepy'"
```bash
pip install -r requirements.txt
# or
pip install moviepy opencv-python pillow
```

### "ffmpeg not found"
```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install ffmpeg

# Linux (Fedora/RHEL)
sudo dnf install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
# Or use: choco install ffmpeg
```

### "ImageMagick is required but not installed"
```bash
# macOS
brew install imagemagick

# Linux (Ubuntu)
sudo apt-get install imagemagick

# Check policy.xml for PDF access
sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' \
  /etc/ImageMagick-6/policy.xml
```

### "ChromeDriver not found" (for ZEE5 crawler)
```bash
# Automatic with webdriver-manager (should be in requirements.txt)
pip install webdriver-manager

# Or download manually:
# https://chromedriver.chromium.org/
# Place in: /usr/local/bin/ or PATH
```

---

## Configuration & Credentials

### "YouTube auth token expired"
**Error:** `YouTube upload failed: invalid_grant`

**Solution:**
```bash
# Delete the old token
rm config/youtube_token.pickle

# Next run will open browser for re-authentication
python main.py --once
```

### "Instagram upload fails with 401 Unauthorized"
**Error:** `Instagram upload failed: 401 Unauthorized`

**Solution:**
1. Check token hasn't expired (valid 60 days)
2. Regenerate token at [facebook.com/developers](https://facebook.com/developers)
3. Verify `INSTAGRAM_BUSINESS_ACCOUNT_ID` is correct
4. Test token: 
```bash
curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_TOKEN"
```

### "ZEE5 login fails"
**Error:** `ZEE5 login failed: ...`

**Solution:**
1. Verify email/password in `.env` (no typos)
2. If password has special chars, escape them: `password123!` → `password123\!`
3. Check ZEE5 account isn't locked (too many login attempts)
4. Try logging in manually at [zee5.com](https://zee5.com) first

### "OpenAI API key rejected"
**Error:** `401 Unauthorized` or `Invalid API key`

**Solution:**
1. Get new key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Verify format: `sk-...` (not old format `sk-ant-...`)
3. Check billing isn't exhausted
4. Verify key isn't rate-limited

---

## Video Processing

### "ffmpeg failed to encode video"
**Error:** `ERROR: Could not write audio and video streams`

**Solution:**
1. Check available disk space: `df -h`
2. Try different video format:
```bash
# In editor/video_editor.py, change codec:
# codec="libx264" → codec="libx265"
```
3. Check video file isn't corrupted:
```bash
ffprobe output/downloads/video.mp4
```

### "Downloaded file is corrupted"
**Error:** `moviepy.video.io.VideoFileClip` error

**Solution:**
```bash
# Delete corrupted file
rm output/downloads/bad_video.mp4

# Run again - will re-download
python main.py --once
```

### "Short is too short or too long"
**Error:** Output video is 30s instead of 58s

**Solution:**
Edit `.env`:
```
SHORT_DURATION=58          # Target duration in seconds
MAX_SOURCE_DURATION=300    # Max source to download (5 min)
```

Then in `editor/video_editor.py`, check `_smart_trim()` logic.

### "Text overlay not showing"
**Error:** Video has no title text overlay

**Solution:**
```bash
# Check if ImageMagick/fonts are missing
apt-get install fonts-dejavu

# Or copy fonts manually:
cp /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf assets/fonts/
```

### "Background music not mixed"
**Error:** Output video has no background music

**Solution:**
1. Add .mp3 files to `assets/music/`:
```bash
# Get free music from Pixabay
curl "https://cdn.pixabay.com/audio/..." -o assets/music/track.mp3
```

2. Or download free tracks:
   - [Pixabay Music](https://pixabay.com/music/)
   - [ccMixter](http://ccmixter.org/)
   - [Free Music Archive](https://freemusicarchive.org/)

---

## Uploading & Posting

### "YouTube upload stuck at 0%"
**Error:** Upload hangs, no progress

**Solution:**
1. Check internet speed: `speedtest-cli`
2. Check YouTube API quota: [console.cloud.google.com/quotas](https://console.cloud.google.com/quotas)
3. Increase timeout in `uploader/youtube_uploader.py`:
```python
# Change from 5MB chunks to 10MB
chunksize=10 * 1024 * 1024
```
4. Try uploading smaller file (edit duration down)

### "Instagram Reel upload fails after 20 min"
**Error:** `Container processing timed out`

**Solution:**
1. **Check video is publicly accessible:**
```bash
# Your INSTAGRAM_MEDIA_HOST_URL must be reachable
curl https://your-url/media/video.mp4
```

2. **Reduce video duration:**
```
INSTAGRAM_MAX_DURATION=59   # Instagram max is 90s
SHORT_DURATION=55
```

3. **Check file size** (Insta has limits):
```bash
ls -lh output/edited/*.mp4
# Should be < 4GB
```

### "YouTube Shorts not published"
**Error:** Video uploads but doesn't appear in Shorts feed

**Reason:** YouTube requires:
- Vertical video (9:16 aspect)
- 15-60 seconds
- Must have audio
- #Shorts hashtag in title/description

**Solution:**
1. Verify dimensions: `ffprobe output/edited/video.mp4 | grep width`
2. Add #Shorts to title: Edit `YT_SHORTS_HASHTAGS` in `config/settings.py`
3. Check audio exists: `ffprobe output/edited/video.mp4 | grep audio`

---

## Background & Daemon

### "Bot stops running after 1 hour"
**Likely cause:** Running in terminal that got closed

**Solution:**
```bash
# Use nohup instead
nohup python main.py > logs/nohup.log 2>&1 &

# Or setup systemd service
sudo cp fifa-shorts-bot.service /etc/systemd/system/
sudo systemctl enable fifa-shorts-bot
sudo systemctl start fifa-shorts-bot
```

### "Systemd service not starting"
**Error:** `systemctl status fifa-shorts-bot` shows failed

**Solution:**
1. Check logs:
```bash
sudo journalctl -u fifa-shorts-bot -n 50
```

2. Verify paths in service file:
```bash
sudo nano /etc/systemd/system/fifa-shorts-bot.service
# Check: WorkingDirectory, ExecStart paths are correct
```

3. Test manually:
```bash
# In the WorkingDirectory, run:
source .venv/bin/activate
python main.py --once
```

4. Fix permissions:
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/fifa-shorts-bot
```

### "High CPU/Memory usage"
**Bot consuming too many resources**

**Solution:**
1. Reduce crawl frequency:
```
CRAWL_INTERVAL_MINUTES=120   # Every 2 hours instead of 30 min
```

2. Reduce videos per run:
```
MAX_SHORTS_PER_RUN=1         # Only 1 short per run
```

3. Monitor resource usage:
```bash
top | grep python
# or
ps aux | grep main.py
```

---

## Cloud Deployment

### "Railway: No Python found"
**Error:** `python: command not found`

**Solution:**
Add `runtime.txt` file:
```
python-3.11
```

Or check Dockerfile uses correct base image.

### "Cloud Run: Build fails"
**Error:** `ERROR: build step "docker build" failed`

**Solution:**
1. Check Dockerfile:
```bash
docker build -t fifa-shorts-bot .
# Run locally first to catch errors
```

2. Check `.gcloudignore`:
```
# Don't upload large files:
output/downloads/
output/edited/
logs/
```

### "Cloud Run: Out of memory"
**Error:** `Exceeded memory allocation`

**Solution:**
```bash
gcloud run deploy fifa-shorts-bot \
  --memory 4Gi    # Increase from 2Gi to 4Gi
```

Or reduce video resolution/duration.

---

## Network & API Issues

### "Download fails: Connection timeout"
**Error:** `TIMEOUT: Reading data from socket`

**Solution:**
```bash
# Increase retry count in downloader/video_downloader.py:
@retry(stop=stop_after_attempt(5), ...)  # Was 3, now 5
```

Or check internet:
```bash
ping youtube.com
speedtest-cli
```

### "API rate limit exceeded"
**Error:** `429 Too Many Requests`

**Solution:**
```
# Increase CRAWL_INTERVAL_MINUTES
CRAWL_INTERVAL_MINUTES=120    # From 30
MAX_SHORTS_PER_RUN=1          # From 3
```

Check quota limits:
- YouTube: 10,000 units/day
- Instagram: Depends on app tier
- OpenAI: Check billing & rate limits

---

## Logs & Debugging

### Enable debug logging
```bash
# In config/settings.py or code:
logger.setLevel(logging.DEBUG)
```

### Check detailed logs
```bash
# Last 50 lines
tail -n 50 logs/bot.log

# Follow in real-time
tail -f logs/bot.log

# Search for errors
grep ERROR logs/bot.log
```

### Test individual components
```bash
# Test YouTube crawler
python -c "from crawler.youtube_crawler import YouTubeCrawler; print(YouTubeCrawler().discover())"

# Test ZEE5 crawler
python -c "from crawler.zee5_crawler import ZEE5Crawler; print(ZEE5Crawler().discover())"

# Test download
python -c "from downloader.video_downloader import VideoDownloader; print(VideoDownloader().download('https://www.youtube.com/watch?v=...'))"
```

---

## Still Stuck?

1. **Check logs:** `tail -f logs/bot.log`
2. **Test locally:** `python main.py --crawl-only`
3. **Verify credentials:** `echo $YOUTUBE_CLIENT_ID` (should show value)
4. **Check network:** `ping google.com`
5. **Restart everything:**
```bash
# Stop
pkill -f "python main.py"
# Or
sudo systemctl restart fifa-shorts-bot

# Clear cache
rm -rf __pycache__ config/__pycache__

# Restart
python main.py --once
```

---

## Performance Tips

```bash
# Speed up video encoding
# In editor/video_editor.py:
composite.write_videofile(..., preset="ultrafast")  # Was "fast"

# Reduce quality for testing
OUTPUT_HEIGHT=1080    # From 1920
OUTPUT_WIDTH=540      # From 1080
SHORT_DURATION=30     # From 58

# Parallel processing (advanced)
# Modify pipeline.py to process multiple videos at once
```

---

Good luck! 🚀

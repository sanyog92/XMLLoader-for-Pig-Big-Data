# 🚀 FIFA 2026 Shorts Bot — Complete Deployment Guide

Deploy and run your bot on **free platforms** with step-by-step instructions. Choose your path below.

---

## 📋 Choose Your Deployment Platform

| Platform | Cost | Setup Time | Best For | Notes |
|----------|------|-----------|----------|-------|
| **Railway** | Free tier (500 hrs/mo) | 5 min | Most beginner-friendly | Card required |
| **Replit** | Free | 5 min | Testing & learning | Limited resources |
| **Heroku** (Legacy Free Tier Ended) | Paid only now | N/A | Not recommended | Sunset Nov 2022 |
| **DigitalOcean App Platform** | $5–12/mo | 10 min | Production-ready | Cheapest paid option |
| **AWS Lightsail** | Free for 1 year | 15 min | Scalable | Needs billing |
| **Google Cloud Run** | Pay-per-use (very cheap) | 15 min | Scalable, serverless | Needs billing |
| **Local + ngrok** | Free (ngrok token) | 3 min | Development | Limited bandwidth |
| **Your own VPS** | $2–5/mo | 20 min | Full control | e.g., Linode, Vultr |

---

## Option 1: Railway (Recommended for Beginners) ⭐

### Prerequisites
- [Railway.app](https://railway.app/) account (sign up with GitHub)
- Your `.env` file with credentials

### Step-by-Step

#### 1.1 Create Railway Account
```bash
# Go to https://railway.app
# Sign up with GitHub (easiest)
# Link your GitHub account
```

#### 1.2 Fork/Push to GitHub
```bash
# Make sure your repo is on GitHub
git remote add origin https://github.com/YOUR_USERNAME/fifa-shorts-bot.git
git branch -M main
git push -u origin main
```

#### 1.3 Create Railway Project
1. Log in to [railway.app](https://railway.app/)
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your **fifa-shorts-bot** repo
4. Click **"Deploy Now"**

#### 1.4 Add Environment Variables
1. Click your deployed project
2. Go to **Settings** → **Variables**
3. Add all from your `.env`:
   ```
   YOUTUBE_CLIENT_ID=...
   YOUTUBE_CLIENT_SECRET=...
   YOUTUBE_REFRESH_TOKEN=...
   INSTAGRAM_ACCESS_TOKEN=...
   INSTAGRAM_BUSINESS_ACCOUNT_ID=...
   INSTAGRAM_MEDIA_HOST_URL=https://your-railway-domain.com/media/
   ZEE5_EMAIL=your_email
   ZEE5_PASSWORD=your_password
   OPENAI_API_KEY=... (optional)
   ```

#### 1.5 Create Procfile (for Railway to know what to run)
```bash
# Create file: Procfile (at project root)
worker: python main.py
```

#### 1.6 Add to requirements.txt (if missing)
```
gunicorn==21.2.0
```

#### 1.7 Commit & Push
```bash
git add Procfile requirements.txt .env
git commit -m "add Railway deployment config"
git push origin main
```

#### 1.8 Check Logs
```bash
# In Railway dashboard, click "Deployments"
# View live logs to confirm it's running
```

**Cost:** Free tier = 500 hours/month (covers 24/7 unless using multiple services)

---

## Option 2: Replit (Easiest, Most Interactive) 🎮

### Prerequisites
- [Replit.com](https://replit.com/) account (free)
- GitHub repo (optional; can paste code directly)

### Step-by-Step

#### 2.1 Create Replit Account
Go to [replit.com](https://replit.com/) → Sign up (GitHub login easiest)

#### 2.2 Create New Repl
1. Click **"+ Create"**
2. Select **"Python"** template
3. Name it: `fifa-shorts-bot`
4. Click **"Create Repl"**

#### 2.3 Clone Your Code
In the terminal:
```bash
git clone https://github.com/YOUR_USERNAME/fifa-shorts-bot.git .
```

#### 2.4 Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2.5 Add Secrets (Environment Variables)
1. Click **🔑 Secrets** (lock icon on left panel)
2. Add each line from your `.env`:
   ```
   YOUTUBE_CLIENT_ID = your_value
   YOUTUBE_CLIENT_SECRET = your_value
   ... (all variables)
   ```

#### 2.6 Create run.sh
```bash
# File: run.sh
#!/bin/bash
python main.py
```

#### 2.7 Run It
```bash
bash run.sh
```

**Cost:** Free (with limits on runtime hours)
**Limitation:** Replit terminates after 1 hour of no activity

---

## Option 3: DigitalOcean App Platform (Production-Ready) 🏆

### Prerequisites
- [DigitalOcean](https://www.digitalocean.com) account
- Credit card ($5 minimum / $12/mo for app)

### Step-by-Step

#### 3.1 Create DigitalOcean Account
- Go to [digitalocean.com](https://www.digitalocean.com)
- Sign up → Add payment method

#### 3.2 Create App
1. Dashboard → **Apps** → **Create App**
2. Select **GitHub** as source
3. Select your `fifa-shorts-bot` repo
4. Click **"Next"**

#### 3.3 Configure
- **Component Name:** `fifa-shorts-bot`
- **Source Type:** `GitHub`
- **Build Command:** (leave empty or `pip install -r requirements.txt`)
- **Run Command:** `python main.py`

#### 3.4 Add Environment Variables
1. Click **"Environment"**
2. Bulk edit (paste all from `.env`):
   ```
   YOUTUBE_CLIENT_ID=...
   YOUTUBE_CLIENT_SECRET=...
   ... (all variables)
   ```

#### 3.5 Deploy
Click **"Create App"** → wait 5 min for deployment

#### 3.6 Check Status
- Apps dashboard → view logs in real-time
- Check pod health

**Cost:** $12/month (includes 3 deployments/month free)

---

## Option 4: Google Cloud Run (Cheapest Scalable Option)

### Prerequisites
- [Google Cloud](https://cloud.google.com) account
- `gcloud` CLI installed

### Step-by-Step

#### 4.1 Create Cloud Project
```bash
gcloud projects create fifa-shorts-bot --name="FIFA 2026 Shorts Bot"
gcloud config set project fifa-shorts-bot
gcloud auth login
```

#### 4.2 Enable APIs
```bash
gcloud services enable run.googleapis.com
```

#### 4.3 Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    chromium \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
```

#### 4.4 Create .gcloudignore
```
__pycache__/
.git/
.env
config/youtube_token.pickle
output/downloads/
output/edited/
logs/
```

#### 4.5 Deploy to Cloud Run
```bash
gcloud run deploy fifa-shorts-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars YOUTUBE_CLIENT_ID=your_value,... \
  --allow-unauthenticated
```

#### 4.6 Monitor
```bash
gcloud run logs read fifa-shorts-bot --region us-central1 --follow
```

**Cost:** Pay-per-use (very cheap — usually < $1/month)

---

## Option 5: Local + ngrok (Development Mode) 🎨

Perfect for testing before deploying to production.

### Prerequisites
- Local machine with Python 3.9+
- [ngrok account](https://ngrok.com) (free)

### Step-by-Step

#### 5.1 Install ngrok
```bash
# macOS
brew install ngrok

# Linux
wget https://bin.equinox.io/c/4VmDzA7iaHg/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin/
```

#### 5.2 Create ngrok Account
- Go to [ngrok.com](https://ngrok.com)
- Sign up (GitHub login)
- Copy your **Auth Token**

#### 5.3 Configure ngrok
```bash
ngrok authtoken YOUR_AUTH_TOKEN
```

#### 5.4 Start HTTP Server (for Instagram uploads)
In one terminal:
```bash
cd output/edited/
python -m http.server 8080
```

#### 5.5 Start ngrok Tunnel
In another terminal:
```bash
ngrok http 8080
```

Copy the HTTPS URL (e.g., `https://1234-56-78-90-123.ngrok.io`)

#### 5.6 Update .env
```
INSTAGRAM_MEDIA_HOST_URL=https://1234-56-78-90-123.ngrok.io/
```

#### 5.7 Run Bot
In another terminal:
```bash
source .venv/bin/activate
python main.py --once --dry-run    # test
python main.py                     # start
```

**Cost:** Free (with 2-hour session limit for free tier)

---

## Option 6: AWS Lightsail (Free for 1 Year) 💰

### Prerequisites
- [AWS account](https://aws.amazon.com)
- Credit card

### Step-by-Step

#### 6.1 Create AWS Account
- Go to [aws.amazon.com](https://aws.amazon.com)
- Sign up → add payment method

#### 6.2 Launch Lightsail Instance
1. Services → **Lightsail**
2. **Create Instance**
3. Platform: **Linux**
4. Blueprint: **Ubuntu 22.04 LTS**
5. Instance Plan: **$3.50/month** (included in free tier first year)
6. Name: `fifa-shorts-bot`
7. **Create Instance**

#### 6.3 Connect via SSH
1. Click your instance
2. **Connect** (browser-based terminal)

#### 6.4 Setup
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip git ffmpeg imagemagick chromium-browser

git clone https://github.com/YOUR_USERNAME/fifa-shorts-bot.git
cd fifa-shorts-bot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 6.5 Add Credentials
```bash
nano .env
# Paste all variables from your .env
# Press Ctrl+X → Y → Enter to save
```

#### 6.6 Run as Background Service
```bash
# Create systemd service
sudo nano /etc/systemd/system/fifa-shorts-bot.service
```

Paste:
```ini
[Unit]
Description=FIFA 2026 Shorts Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/fifa-shorts-bot
ExecStart=/home/ubuntu/fifa-shorts-bot/.venv/bin/python main.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fifa-shorts-bot
sudo systemctl start fifa-shorts-bot
sudo journalctl -fu fifa-shorts-bot
```

**Cost:** $3.50/month (free first 12 months with eligible account)

---

## Option 7: Your Own VPS (Linode / Vultr) 🖥️

Cheapest paid option for long-term use.

### Prerequisites
- [Linode](https://linode.com) or [Vultr](https://vultr.com) account
- $2–5/month

### Quick Steps
```bash
# 1. Create Linode instance (Ubuntu 22.04, $5/mo)
# 2. SSH in
ssh root@YOUR_IP

# 3. Setup
apt-get update && apt-get install -y python3-pip git ffmpeg imagemagick chromium-browser

git clone https://github.com/YOUR_USERNAME/fifa-shorts-bot.git
cd fifa-shorts-bot

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Create .env with nano
nano .env
# (paste all credentials)

# 5. Create systemd service (see AWS Lightsail section above)
# 6. Start it
sudo systemctl start fifa-shorts-bot
```

**Cost:** $2.50–5/month (includes root access)

---

## 🔐 Securing Your Credentials on Cloud Platforms

**NEVER commit `.env` to GitHub!** Use platform-specific secret management:

### Railway
- Settings → **Variables** (UI)
- Automatically encrypted

### Replit
- Click 🔑 **Secrets** (UI)
- Not visible in logs

### DigitalOcean
- App Settings → **Environment**
- Encrypted at rest

### Cloud Run
- Create `secrets.yaml` in Cloud Secret Manager
```bash
gcloud secrets create youtube-client-id --data-file=- <<< "YOUR_VALUE"
```

### AWS Lightsail
- Add to `.env` file via SSH
- `.env` should NOT be committed to git

---

## 🧪 Testing & Debugging

### Before Deploying

```bash
# Test locally
python main.py --crawl-only                 # See what it discovers
python main.py --once --dry-run            # Full pipeline, no uploads
```

### After Deploying

#### Railway
```bash
# View logs
railway logs
```

#### Cloud Run
```bash
gcloud run logs read fifa-shorts-bot --follow
```

#### AWS Lightsail
```bash
sudo journalctl -fu fifa-shorts-bot -n 50
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -r requirements.txt` again |
| "ffmpeg not found" | Install: `apt-get install ffmpeg` |
| "Auth token expired" | Refresh token in `.env` |
| "No disk space" | Delete old files: `rm -rf output/downloads/*` |

---

## 📊 Monitoring & Auto-Restart

### Railway
- Built-in auto-restart on failure

### Cloud Run
- Enable auto-scaling in settings

### AWS Lightsail / VPS
```bash
# Systemd auto-restarts on failure
RestartSec=60  # restarts after 60 seconds
```

---

## 💾 Backing Up Your Data

### Output Files (edited shorts)
```bash
# On Cloud Run / Railway
# Configure Cloud Storage bucket

# On AWS Lightsail
aws s3 cp output/edited/ s3://my-fifa-bucket/
```

### Processed IDs Log
```bash
# Keep output/processed_ids.json safe
# (prevents re-uploading same videos)
```

---

## 🎯 Summary: Quick Reference

| Step | Command |
|------|---------|
| 1. Clone repo | `git clone ...` |
| 2. Install deps | `pip install -r requirements.txt` |
| 3. Setup `.env` | `cp .env.example .env && nano .env` |
| 4. Test locally | `python main.py --once --dry-run` |
| 5. Commit | `git add . && git commit -m "..."` |
| 6. Push | `git push origin main` |
| 7. Deploy | Use Railway / Cloud Run / Lightsail (see above) |
| 8. Monitor | View platform logs |
| 9. Enjoy! | Your bot is live 24/7 ✅ |

---

## 📞 Need Help?

1. Check logs: `journalctl -fu fifa-shorts-bot` or platform dashboard
2. Test locally first: `python main.py --crawl-only`
3. Verify credentials: ensure all `.env` vars are set
4. Check internet: API calls need network access
5. Monitor API rate limits (YouTube, Instagram, OpenAI)

Good luck! 🚀⚽

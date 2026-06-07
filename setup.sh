#!/usr/bin/env bash
# One-shot setup script for FIFA 2026 Shorts Bot
set -e

echo "=== FIFA 2026 Shorts Bot — Setup ==="

# Python check
python3 --version || { echo "Python 3.9+ required"; exit 1; }

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install ffmpeg (required by moviepy)
if ! command -v ffmpeg &>/dev/null; then
    echo "Installing ffmpeg..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y ffmpeg
    elif command -v brew &>/dev/null; then
        brew install ffmpeg
    else
        echo "WARNING: ffmpeg not found. Install it manually: https://ffmpeg.org"
    fi
fi

# Install ImageMagick (required by MoviePy TextClip)
if ! command -v convert &>/dev/null; then
    echo "Installing ImageMagick..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y imagemagick
        # Allow PDF operations (needed by some distros)
        sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' \
            /etc/ImageMagick-6/policy.xml 2>/dev/null || true
    elif command -v brew &>/dev/null; then
        brew install imagemagick
    fi
fi

# Create .env if not present
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo ">>> .env created from .env.example"
    echo ">>> Edit .env and add your API credentials, then run:"
    echo ">>>   source .venv/bin/activate"
    echo ">>>   python main.py --once --dry-run   # test"
    echo ">>>   python main.py                    # start scheduler"
fi

echo ""
echo "=== Setup complete! ==="

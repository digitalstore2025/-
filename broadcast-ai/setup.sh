#!/usr/bin/env bash
# ============================================================================
# Quran-Conditioned Palestinian Broadcast AI — Setup Script
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo " Palestinian AI Broadcast — Full Setup"
echo "============================================"
echo ""

# --- Python version check ----------------------------------------------------
echo "[1/5] Checking Python version..."
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is required but not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
echo "  [OK] Python $PYTHON_VERSION detected"

# --- System dependencies ----------------------------------------------------
echo ""
echo "[2/5] Installing system packages..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg
    echo "  [OK] ffmpeg installed via apt-get"
elif command -v yum &>/dev/null; then
    sudo yum install -y ffmpeg
    echo "  [OK] ffmpeg installed via yum"
elif command -v brew &>/dev/null; then
    brew install ffmpeg
    echo "  [OK] ffmpeg installed via brew"
else
    echo "  [WARN] Cannot detect package manager. Install ffmpeg manually."
fi

# Verify ffmpeg
if command -v ffmpeg &>/dev/null; then
    echo "  [OK] ffmpeg verified: $(ffmpeg -version 2>&1 | head -1)"
else
    echo "  [!!] ffmpeg not found — audio/video processing will fail"
fi

# --- Python dependencies ----------------------------------------------------
echo ""
echo "[3/5] Installing Python dependencies..."
pip3 install -q -r requirements.txt
echo "  [OK] Python packages installed"

# Verify core imports
python3 -c "import TTS; print('  [OK] TTS', TTS.__version__)" 2>/dev/null || echo "  [!!] TTS import failed"
python3 -c "import torch; print('  [OK] PyTorch', torch.__version__)" 2>/dev/null || echo "  [!!] PyTorch import failed"
python3 -c "import flask; print('  [OK] Flask', flask.__version__)" 2>/dev/null || echo "  [!!] Flask import failed"
python3 -c "import feedparser; print('  [OK] feedparser')" 2>/dev/null || echo "  [!!] feedparser import failed"

# --- Directory structure -----------------------------------------------------
echo ""
echo "[4/5] Creating directory structure..."
dirs=(
    dataset_quran/wavs
    dataset_speaker/wavs
    dataset_speaker_news/wavs
    dataset_speaker_palestinian/wavs
    dataset_speaker_realistic/wavs
    dataset_authority/wavs
    models
    output/episodes
    output/voiceovers
    input
    logs
    cache
)

for d in "${dirs[@]}"; do
    mkdir -p "$d"
done
echo "  [OK] Directory structure ready"

# --- Create example CSV files -----------------------------------------------
echo ""
echo "[5/5] Verifying example metadata files..."
for dataset in dataset_quran dataset_speaker dataset_speaker_news dataset_speaker_palestinian dataset_speaker_realistic dataset_authority; do
    if [ -f "$dataset/metadata.csv.example" ]; then
        echo "  [OK] $dataset/metadata.csv.example"
    fi
done

# --- Wav2Lip (optional) -----------------------------------------------------
echo ""
echo "[--] Wav2Lip setup (optional)..."
if [ -f "Wav2Lip/inference.py" ]; then
    echo "  [OK] Wav2Lip already installed"
else
    echo "  [--] Wav2Lip not installed (video lip-sync disabled)"
    echo "  [--] Run: bash setup_wav2lip.sh   to install"
fi

# --- Summary -----------------------------------------------------------------
echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo ""
echo " Project structure:"
echo "   broadcast-ai/"
echo "   ├── config.py            — Configuration"
echo "   ├── train.py             — Model training"
echo "   ├── generate.py          — Voice synthesis"
echo "   ├── run_tv_channel.py    — TV broadcast loop"
echo "   ├── radio_station.py     — Radio broadcast"
echo "   ├── podcast_generator.py — Podcast episodes"
echo "   ├── voiceover.py         — Voiceover engine"
echo "   ├── scheduler.py         — Schedule manager"
echo "   ├── rss_feed.py          — RSS news integration"
echo "   ├── tv_server.py         — Web server"
echo "   └── main.py              — Unified launcher"
echo ""
echo " Quick start:"
echo "   1. Add WAV + metadata.csv to dataset_* dirs"
echo "   2. python3 train.py"
echo "   3. python3 main.py"
echo "      -> Web UI at http://localhost:3000"
echo ""
echo " Or run individual services:"
echo "   python3 main.py --all        TV + Radio + Server"
echo "   python3 main.py --radio      Radio + Server"
echo "   python3 main.py --server     Server only"
echo "   python3 main.py --podcast    Generate episode"
echo ""

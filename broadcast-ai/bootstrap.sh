#!/usr/bin/env bash
# ============================================================================
# Quran-Conditioned Palestinian Broadcast AI — One-Command Bootstrap
#
# Downloads everything needed and starts the system in demo mode.
#
# Usage:
#   bash bootstrap.sh           Full setup + demo
#   bash bootstrap.sh --quick   Skip Quran download, demo only
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

QUICK_MODE=false
if [[ "${1:-}" == "--quick" ]]; then
    QUICK_MODE=true
fi

echo ""
echo "  ====================================================="
echo "  Palestinian AI Broadcast System — Bootstrap"
echo "  ====================================================="
echo ""

# --- Step 1: ffmpeg ---
echo "[1/5] Setting up ffmpeg..."
if command -v ffmpeg &>/dev/null; then
    echo "  [OK] ffmpeg already available"
else
    echo "  Installing ffmpeg via pip (imageio-ffmpeg)..."
    pip3 install --quiet imageio-ffmpeg 2>/dev/null
    FFMPEG_PATH=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" 2>/dev/null)
    if [ -n "$FFMPEG_PATH" ] && [ -f "$FFMPEG_PATH" ]; then
        ln -sf "$FFMPEG_PATH" /usr/local/bin/ffmpeg 2>/dev/null || true
        echo "  [OK] ffmpeg installed via imageio-ffmpeg"
    else
        echo "  [!!] ffmpeg installation failed — some features may not work"
    fi
fi

# --- Step 2: Python dependencies ---
echo ""
echo "[2/5] Installing Python dependencies..."
pip3 install --quiet --ignore-installed flask numpy scipy soundfile atoma imageio-ffmpeg ffmpeg-python 2>&1 | tail -3

# Install TTS + torch (large download)
echo "  Installing TTS + PyTorch (this may take several minutes)..."
pip3 install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cpu 2>&1 | tail -3
pip3 install --quiet TTS==0.22.0 2>&1 | tail -3

# Verify
echo ""
echo "  Verifying installations..."
python3 -c "import flask; print('  [OK] Flask')" 2>/dev/null || echo "  [!!] Flask missing"
python3 -c "import torch; print('  [OK] PyTorch', torch.__version__)" 2>/dev/null || echo "  [!!] PyTorch missing"
python3 -c "import TTS; print('  [OK] TTS')" 2>/dev/null || { echo "  [!!] TTS missing"; exit 1; }
python3 -c "import atoma; print('  [OK] atoma (RSS)')" 2>/dev/null || echo "  [!!] atoma missing"

# --- Step 3: Directory structure ---
echo ""
echo "[3/5] Creating directories..."
mkdir -p dataset_quran/wavs dataset_speaker/wavs dataset_speaker_news/wavs \
         dataset_speaker_palestinian/wavs dataset_speaker_realistic/wavs \
         dataset_authority/wavs models output/episodes output/voiceovers \
         input logs cache
echo "  [OK] All directories ready"

# --- Step 4: Quran dataset ---
echo ""
if [ "$QUICK_MODE" = true ]; then
    echo "[4/5] Skipping Quran download (--quick mode)"
else
    echo "[4/5] Downloading Quran dataset (Al-Fatiha + short surahs)..."
    python3 download_quran_dataset.py --surah 1 112 113 114 103 108 110 2>&1 | grep -E "^\[|Done" || echo "  [!!] Download encountered issues (may work offline)"
fi

# --- Step 5: Launch demo ---
echo ""
echo "[5/5] Launching demo mode..."
echo ""
echo "  ====================================================="
echo "  SYSTEM READY!"
echo "  ====================================================="
echo ""
echo "  Starting demo broadcast with pre-trained XTTS v2..."
echo "  Web UI will be at: http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

python3 demo.py

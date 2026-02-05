#!/usr/bin/env bash
# ============================================================================
# Quran-Conditioned Palestinian Broadcast AI — Setup Script
# ============================================================================
set -euo pipefail

echo "============================================"
echo " Palestinian AI Broadcast — Setup"
echo "============================================"

# --- System dependencies ----------------------------------------------------
echo "[1/3] Installing system packages..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg
elif command -v yum &>/dev/null; then
    sudo yum install -y ffmpeg
else
    echo "[WARN] Cannot detect package manager. Install ffmpeg manually."
fi

# --- Python dependencies ----------------------------------------------------
echo "[2/3] Installing Python dependencies..."
pip install -q -r requirements.txt

# --- Directory structure -----------------------------------------------------
echo "[3/3] Verifying directory structure..."
dirs=(
    dataset_quran/wavs
    dataset_speaker/wavs
    dataset_speaker_news/wavs
    dataset_speaker_palestinian/wavs
    dataset_speaker_realistic/wavs
    dataset_authority/wavs
    models
    output
    input
)

for d in "${dirs[@]}"; do
    mkdir -p "$d"
done

echo ""
echo "============================================"
echo " Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Add WAV files and metadata.csv to each dataset_* directory"
echo "     (see *.csv.example files for the format)"
echo "  2. Place an anchor image at input/anchor.jpg"
echo "  3. Run:  python train.py"
echo "  4. Run:  python run_tv_channel.py   (Terminal 1)"
echo "  5. Run:  python tv_server.py         (Terminal 2)"
echo ""

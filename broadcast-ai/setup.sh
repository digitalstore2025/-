#!/usr/bin/env bash
# ============================================================================
# Quran-Conditioned Palestinian Broadcast AI — Setup Script
# ============================================================================
set -euo pipefail

echo "============================================"
echo " Palestinian AI Broadcast — Setup"
echo "============================================"

# --- Python version check ----------------------------------------------------
echo "[1/5] Checking Python version..."
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is required but not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# --- System dependencies ----------------------------------------------------
echo "[2/5] Installing system packages..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq ffmpeg
    echo "✓ ffmpeg installed via apt-get"
elif command -v yum &>/dev/null; then
    sudo yum install -y ffmpeg
    echo "✓ ffmpeg installed via yum"
elif command -v brew &>/dev/null; then
    brew install ffmpeg
    echo "✓ ffmpeg installed via brew"
else
    echo "[WARN] Cannot detect package manager. Install ffmpeg manually."
fi

# Verify ffmpeg installation
if command -v ffmpeg &>/dev/null; then
    echo "✓ ffmpeg verified: $(ffmpeg -version | head -n1)"
else
    echo "[WARN] ffmpeg not found in PATH. Some features may not work."
fi

# --- Python dependencies ----------------------------------------------------
echo "[3/5] Installing Python dependencies..."
pip3 install -q -r requirements.txt
echo "✓ Python packages installed"

# --- Directory structure -----------------------------------------------------
echo "[4/5] Creating directory structure..."
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
echo "✓ Directory structure ready"

# --- Create example CSV files -----------------------------------------------
echo "[5/5] Creating example metadata files..."
for dataset in dataset_quran dataset_speaker dataset_speaker_news dataset_speaker_palestinian dataset_speaker_realistic dataset_authority; do
    if [ ! -f "$dataset/metadata.csv.example" ]; then
        cat > "$dataset/metadata.csv.example" << 'EOF'
audio_001.wav|النص العربي هنا
audio_002.wav|مثال آخر للنص العربي
EOF
        echo "✓ Created $dataset/metadata.csv.example"
    fi
done

echo ""
echo "============================================"
echo " ✓ Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Add WAV files and metadata.csv to each dataset_* directory"
echo "     (see *.csv.example files for the format)"
echo "  2. Place an anchor image at input/anchor.jpg"
echo "  3. Run:  python3 train.py"
echo "  4. Run:  python3 run_tv_channel.py   (Terminal 1)"
echo "  5. Run:  python3 tv_server.py         (Terminal 2)"
echo ""

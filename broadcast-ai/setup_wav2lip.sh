#!/usr/bin/env bash
# ============================================================================
# Wav2Lip — Automated Installation for Palestinian Broadcast AI
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WAV2LIP_DIR="$SCRIPT_DIR/Wav2Lip"
MODELS_DIR="$SCRIPT_DIR/models"

echo "============================================"
echo " Wav2Lip — Automated Setup"
echo "============================================"

# --- Clone Wav2Lip ---
if [ -d "$WAV2LIP_DIR" ]; then
    echo "[1/4] Wav2Lip directory already exists, pulling latest..."
    cd "$WAV2LIP_DIR" && git pull || true
    cd "$SCRIPT_DIR"
else
    echo "[1/4] Cloning Wav2Lip repository..."
    git clone https://github.com/Rudrabha/Wav2Lip.git "$WAV2LIP_DIR"
fi

# --- Install Wav2Lip dependencies ---
echo "[2/4] Installing Wav2Lip Python dependencies..."
pip install -q -r "$WAV2LIP_DIR/requirements.txt" 2>/dev/null || {
    echo "[WARN] Some Wav2Lip deps failed. Installing core packages manually..."
    pip install -q librosa numpy opencv-python-headless
}

# --- Download pre-trained model ---
echo "[3/4] Downloading Wav2Lip pre-trained model..."
mkdir -p "$MODELS_DIR"

WAV2LIP_MODEL="$MODELS_DIR/wav2lip.pth"

if [ -f "$WAV2LIP_MODEL" ]; then
    echo "       Model already downloaded."
else
    echo "       Downloading wav2lip.pth (416 MB)..."
    echo ""
    echo "  NOTE: If auto-download fails, manually download from:"
    echo "  https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80YsvvDUa7B1iaA?e=TBFBVW"
    echo "  and place it at: $WAV2LIP_MODEL"
    echo ""

    # Try gdown first (Google Drive alternative links)
    if command -v gdown &>/dev/null; then
        gdown --fuzzy "https://drive.google.com/file/d/1gm8VG_K_AaWgNFTlNPMEjCDaJQy_Kze1/view" -O "$WAV2LIP_MODEL" || true
    fi

    if [ ! -f "$WAV2LIP_MODEL" ]; then
        echo "[WARN] Auto-download failed. Please download manually."
        echo "       Place wav2lip.pth at: $WAV2LIP_MODEL"
    fi
fi

# --- Verify installation ---
echo "[4/4] Verifying installation..."

ERRORS=0

if [ -f "$WAV2LIP_DIR/inference.py" ]; then
    echo "  [OK] Wav2Lip inference.py found"
else
    echo "  [!!] Wav2Lip inference.py NOT found"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$WAV2LIP_MODEL" ]; then
    echo "  [OK] wav2lip.pth model found"
else
    echo "  [!!] wav2lip.pth model NOT found"
    ERRORS=$((ERRORS + 1))
fi

python -c "import cv2; print('  [OK] OpenCV:', cv2.__version__)" 2>/dev/null || {
    echo "  [!!] OpenCV not available"
    ERRORS=$((ERRORS + 1))
}

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo "============================================"
    echo " Wav2Lip setup COMPLETE"
    echo "============================================"
else
    echo "============================================"
    echo " Wav2Lip setup PARTIAL ($ERRORS issues)"
    echo " System will fall back to audio-only mode"
    echo "============================================"
fi

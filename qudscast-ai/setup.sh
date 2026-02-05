#!/bin/bash
# QudsCast AI - Setup Script
set -e

echo "========================================"
echo "  QudsCast AI - Setup"
echo "========================================"

# Check Node.js version
echo "[1/7] Checking Node.js version..."
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "ERROR: Node.js 18+ is required (found: $(node --version))"
    exit 1
fi
echo "✓ Node.js $(node --version) detected"

# Setup environment file
echo "[2/7] Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
else
    echo "✓ .env already exists"
fi

# Create storage directories
echo "[3/7] Creating storage directories..."
mkdir -p storage/voices storage/jingles storage/audio storage/videos
echo "✓ Storage directories ready"

# Install all dependencies
echo "[4/7] Installing dependencies..."
npm run install:all

# Build frontend
echo "[5/7] Building frontend..."
cd frontend && npm run build && cd ..
echo "✓ Frontend build complete"

# Install Python dependencies (optional)
echo "[6/7] Installing Python TTS dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install gtts 2>/dev/null && echo "✓ Python TTS installed" || echo "⚠ Python TTS installation skipped"
elif command -v pip &>/dev/null; then
    pip install gtts 2>/dev/null && echo "✓ Python TTS installed" || echo "⚠ Python TTS installation skipped"
else
    echo "⚠ pip not found - Python TTS installation skipped"
fi

# Make scripts executable
echo "[7/7] Setting script permissions..."
chmod +x backend/audio/generate_radio_mp3.sh
chmod +x backend/video/generate_video.sh
chmod +x backend/tts/generate_voice.py
echo "✓ Scripts are executable"

echo ""
echo "========================================"
echo "  ✓ Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  npm run start"
echo ""
echo "Or for development:"
echo "  npm run dev"
echo ""

#!/bin/bash
# QudsCast AI - Setup Script

echo "========================================"
echo "  QudsCast AI - Setup"
echo "========================================"

# Install backend dependencies
echo "Installing backend dependencies..."
npm install

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Build frontend
echo "Building frontend..."
cd frontend && npm run build && cd ..

# Install Python dependencies (optional)
echo "Installing Python TTS dependencies..."
pip install gtts 2>/dev/null || pip3 install gtts 2>/dev/null || echo "Python TTS installation skipped"

# Make scripts executable
chmod +x backend/audio/generate_radio_mp3.sh
chmod +x backend/video/generate_video.sh
chmod +x backend/tts/generate_voice.py

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  npm run start"
echo ""
echo "Or for development:"
echo "  npm run dev"
echo ""

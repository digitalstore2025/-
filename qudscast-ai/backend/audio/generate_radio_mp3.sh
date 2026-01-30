#!/bin/bash
# QudsCast AI - Radio MP3 Generator
# Merges intro jingle + voice + outro jingle with audio normalization

set -e

# Arguments
INTRO="${1:-storage/jingles/intro.mp3}"
VOICE="${2:-storage/audio/voice.wav}"
OUTRO="${3:-storage/jingles/outro.mp3}"
OUTPUT="${4:-storage/audio/final_radio.mp3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "========================================"
echo "QudsCast AI - Radio MP3 Generator"
echo "========================================"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: FFmpeg is not installed${NC}"
    exit 1
fi

# Create default jingles if they don't exist
if [ ! -f "$INTRO" ]; then
    echo "Creating default intro jingle..."
    mkdir -p "$(dirname "$INTRO")"
    ffmpeg -y -f lavfi -i "anullsrc=r=44100:cl=stereo" -t 2 "$INTRO" 2>/dev/null
fi

if [ ! -f "$OUTRO" ]; then
    echo "Creating default outro jingle..."
    mkdir -p "$(dirname "$OUTRO")"
    ffmpeg -y -f lavfi -i "anullsrc=r=44100:cl=stereo" -t 2 "$OUTRO" 2>/dev/null
fi

# Check voice file
if [ ! -f "$VOICE" ]; then
    # Try mp3 version
    VOICE_MP3="${VOICE%.wav}.mp3"
    if [ -f "$VOICE_MP3" ]; then
        VOICE="$VOICE_MP3"
    else
        echo -e "${RED}Error: Voice file not found: $VOICE${NC}"
        exit 1
    fi
fi

# Create output directory
mkdir -p "$(dirname "$OUTPUT")"

echo "Processing:"
echo "  Intro: $INTRO"
echo "  Voice: $VOICE"
echo "  Outro: $OUTRO"
echo "  Output: $OUTPUT"

# Method 1: Full processing with loudnorm
echo "Generating radio MP3 with normalization..."
if ffmpeg -y \
    -i "$INTRO" \
    -i "$VOICE" \
    -i "$OUTRO" \
    -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[outa]" \
    -map "[outa]" \
    -codec:a libmp3lame \
    -b:a 192k \
    "$OUTPUT" 2>/dev/null; then
    echo -e "${GREEN}Success: Radio MP3 generated${NC}"
else
    # Method 2: Simple concatenation without normalization
    echo "Fallback: Simple concatenation..."
    ffmpeg -y \
        -i "$INTRO" \
        -i "$VOICE" \
        -i "$OUTRO" \
        -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[outa]" \
        -map "[outa]" \
        -codec:a libmp3lame \
        -b:a 192k \
        "$OUTPUT"
    echo -e "${GREEN}Success: Radio MP3 generated (without normalization)${NC}"
fi

# Show file info
if [ -f "$OUTPUT" ]; then
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null || echo "unknown")
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo ""
    echo "Output Details:"
    echo "  File: $OUTPUT"
    echo "  Size: $SIZE"
    echo "  Duration: ${DURATION}s"
fi

echo "========================================"
echo "Done!"

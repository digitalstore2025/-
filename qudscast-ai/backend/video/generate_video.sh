#!/bin/bash
# QudsCast AI - Video Generator
# Creates 9:16 vertical video with background, zoompan effect, and text overlay

set -e

# Arguments
BACKGROUND="${1:-storage/bg.jpg}"
AUDIO="${2:-storage/audio/final_radio.mp3}"
CAPTION="${3:-أخبار إذاعة القدس}"
OUTPUT="${4:-storage/videos/final_video.mp4}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "QudsCast AI - Video Generator (9:16)"
echo "========================================"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: FFmpeg is not installed${NC}"
    exit 1
fi

# Create default background if not exists
if [ ! -f "$BACKGROUND" ]; then
    echo "Creating default background..."
    mkdir -p "$(dirname "$BACKGROUND")"
    # Create a dark gradient background
    ffmpeg -y -f lavfi -i "color=c=#1a1a2e:s=1080x1920:d=1" \
        -vf "drawtext=text='إذاعة القدس':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=h/2-36" \
        -vframes 1 "$BACKGROUND" 2>/dev/null || \
    ffmpeg -y -f lavfi -i "color=c=#1a1a2e:s=1080x1920:d=1" -vframes 1 "$BACKGROUND"
fi

# Check audio file
if [ ! -f "$AUDIO" ]; then
    echo -e "${RED}Error: Audio file not found: $AUDIO${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$(dirname "$OUTPUT")"

# Get audio duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO" 2>/dev/null || echo "30")
DURATION=$(echo "$DURATION" | cut -d. -f1)
DURATION=$((DURATION + 1))

echo "Processing:"
echo "  Background: $BACKGROUND"
echo "  Audio: $AUDIO"
echo "  Duration: ${DURATION}s"
echo "  Output: $OUTPUT"

# Escape caption for FFmpeg
ESCAPED_CAPTION=$(echo "$CAPTION" | sed "s/'/'\\\\''/g" | sed 's/:/\\:/g' | cut -c1-200)

# Calculate frames for zoompan
FRAMES=$((DURATION * 25))

echo "Generating 9:16 video..."

# Method 1: Full video with text overlay
if ffmpeg -y -loop 1 -i "$BACKGROUND" -i "$AUDIO" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,zoompan=z='min(zoom+0.0003,1.03)':d=$FRAMES:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',drawbox=y=ih-280:color=black@0.7:width=iw:height=180:t=fill" \
    -t "$DURATION" \
    -c:v libx264 \
    -preset fast \
    -crf 23 \
    -c:a aac \
    -b:a 128k \
    -pix_fmt yuv420p \
    -shortest \
    "$OUTPUT" 2>/dev/null; then
    echo -e "${GREEN}Success: Video generated${NC}"
else
    # Method 2: Simple video without effects
    echo -e "${YELLOW}Fallback: Generating simple video...${NC}"
    ffmpeg -y -loop 1 -i "$BACKGROUND" -i "$AUDIO" \
        -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
        -t "$DURATION" \
        -c:v libx264 \
        -preset fast \
        -c:a aac \
        -pix_fmt yuv420p \
        -shortest \
        "$OUTPUT"
    echo -e "${GREEN}Success: Simple video generated${NC}"
fi

# Show file info
if [ -f "$OUTPUT" ]; then
    FILESIZE=$(du -h "$OUTPUT" | cut -f1)
    RESOLUTION=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$OUTPUT" 2>/dev/null || echo "unknown")
    echo ""
    echo "Output Details:"
    echo "  File: $OUTPUT"
    echo "  Size: $FILESIZE"
    echo "  Resolution: $RESOLUTION"
    echo "  Duration: ${DURATION}s"
fi

echo "========================================"
echo "Done!"

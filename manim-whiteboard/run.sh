#!/bin/bash
# Quick render script for Manim Whiteboard

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Manim Whiteboard Renderer ===${NC}"
echo ""

# Check if manim is installed
if ! command -v manim &> /dev/null; then
    echo -e "${RED}Error: Manim is not installed${NC}"
    echo "Install with: pip install manim"
    exit 1
fi

# Default values
QUALITY="l"
SCENE="GazaWhiteboardMap"
FILE="scenes/gaza_whiteboard.py"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quality)
            QUALITY="$2"
            shift 2
            ;;
        -s|--scene)
            SCENE="$2"
            shift 2
            ;;
        -f|--file)
            FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -q, --quality  Quality: l(ow), m(edium), h(igh), k(4K)"
            echo "  -s, --scene    Scene name (default: GazaWhiteboardMap)"
            echo "  -f, --file     Python file (default: scenes/gaza_whiteboard.py)"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                         # Quick preview"
            echo "  ./run.sh -q h                    # 1080p render"
            echo "  ./run.sh -q k -s MinimalGazaMap  # 4K minimal version"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}Rendering: ${SCENE}${NC}"
echo -e "${YELLOW}Quality: ${QUALITY}${NC}"
echo -e "${YELLOW}File: ${FILE}${NC}"
echo ""

# Run manim
cd "$(dirname "$0")"
manim -pq${QUALITY} ${FILE} ${SCENE}

echo ""
echo -e "${GREEN}Done! Check media/videos/ for output.${NC}"

# Manim Whiteboard Animation Engine

Professional whiteboard-style video generation using Python and Manim.

## Features

- Hand-drawn sketch effects for maps and shapes
- Geographic data for Gaza Strip and West Bank
- Reusable templates for custom content
- Multiple output qualities (480p to 4K)
- Arabic text support

## Quick Start

### 1. Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y build-essential python3-dev libcairo2-dev \
    libpango1.0-dev ffmpeg texlive texlive-latex-extra

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Render Your First Video

```bash
# Preview quality (fast, 480p)
manim -pql scenes/gaza_whiteboard.py GazaWhiteboardMap

# Production quality (1080p)
manim -pqh scenes/gaza_whiteboard.py GazaWhiteboardMap

# 4K quality
manim -pqk scenes/gaza_whiteboard.py GazaWhiteboardMap
```

### 3. Output Location

Videos are saved to: `media/videos/`

## Available Scenes

| Scene | Description | Command |
|-------|-------------|---------|
| `GazaWhiteboardMap` | Full animated map with cities and stats | `manim -pqh scenes/gaza_whiteboard.py GazaWhiteboardMap` |
| `GazaTimelineAnimation` | Historical timeline | `manim -pqh scenes/gaza_whiteboard.py GazaTimelineAnimation` |
| `MinimalGazaMap` | Simple, quick version | `manim -pql scenes/gaza_whiteboard.py MinimalGazaMap` |
| `WhiteboardTemplate` | Reusable template | `manim -pql scenes/custom_template.py WhiteboardTemplate` |

## Project Structure

```
manim-whiteboard/
|-- scenes/
|   |-- gaza_whiteboard.py    # Main animation scenes
|   |-- custom_template.py    # Reusable templates
|-- utils/
|   |-- colors.py             # Color palettes
|   |-- map_data.py           # Geographic coordinates
|   |-- sketch_effects.py     # Hand-drawn effects
|-- assets/
|   |-- svg/                  # SVG files for detailed maps
|   |-- audio/                # Audio files for narration
|-- output/                   # Rendered videos
|-- requirements.txt
|-- README.md
```

## Customization

### Adding New Maps

Edit `utils/map_data.py` to add coordinates for new regions:

```python
NEW_REGION_COORDINATES = [
    (x1, y1, 0),
    (x2, y2, 0),
    # ... more points
]
```

### Changing Colors

Edit `utils/colors.py`:

```python
WHITEBOARD_COLORS = {
    'background': '#FFFFFF',      # Change background
    'marker_black': '#1A1A1A',    # Change marker color
    # ...
}
```

### Custom Sketch Effects

Use the `SketchyPolygon` class with roughness parameter:

```python
from utils.sketch_effects import SketchyPolygon

shape = SketchyPolygon(
    *coordinates,
    roughness=0.05,  # 0.0 = perfect, 0.1 = very sketchy
    stroke_width=4
)
```

## Render Options

| Flag | Quality | Resolution | Use Case |
|------|---------|------------|----------|
| `-ql` | Low | 480p, 15fps | Quick preview |
| `-qm` | Medium | 720p, 30fps | Draft review |
| `-qh` | High | 1080p, 60fps | Production |
| `-qk` | 4K | 2160p, 60fps | Cinema quality |

### Additional Flags

```bash
-p              # Preview after render
-a              # Render all scenes in file
--format gif    # Output as GIF
-s              # Save last frame as PNG
```

## Example: Creating a Custom Video

```python
from manim import *
from utils.sketch_effects import SketchyPolygon
from utils.colors import WHITEBOARD_COLORS

class MyCustomScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # Your content here
        title = Text("My Video", font_size=48, color=BLACK)
        self.play(Write(title))
        self.wait(2)
```

Run with:
```bash
manim -pqh my_scene.py MyCustomScene
```

## Troubleshooting

### "No module named 'manim'"
```bash
pip install manim
```

### Arabic text not rendering
Install Arabic fonts:
```bash
sudo apt install fonts-noto-arabic
```

### Video playback issues
Ensure ffmpeg is installed:
```bash
sudo apt install ffmpeg
```

## License

MIT License - Free for personal and commercial use.

"""
Whiteboard-style color palettes for Manim animations.
Optimized for educational and documentary content.
"""

from manim import ManimColor

# Whiteboard Theme Colors
WHITEBOARD_COLORS = {
    # Background
    'background': '#FFFFFF',
    'background_cream': '#FDF6E3',
    'background_paper': '#F5F5DC',

    # Primary Drawing Colors
    'marker_black': '#1A1A1A',
    'marker_blue': '#2E5090',
    'marker_red': '#C41E3A',
    'marker_green': '#228B22',
    'marker_orange': '#FF6B35',

    # Geographic Colors
    'sea_blue': '#4A90D9',
    'sea_light': '#87CEEB',
    'land_beige': '#F5DEB3',
    'border_red': '#DC143C',
    'highlight_yellow': '#FFD700',

    # Text Colors
    'text_primary': '#2C3E50',
    'text_secondary': '#7F8C8D',
    'text_accent': '#E74C3C',

    # Shadow & Depth
    'shadow': '#CCCCCC',
    'shadow_dark': '#999999',
}

# Sketch Effect Parameters
SKETCH_PARAMS = {
    'stroke_width_thin': 2,
    'stroke_width_medium': 4,
    'stroke_width_thick': 6,
    'roughness_low': 0.02,
    'roughness_medium': 0.05,
    'roughness_high': 0.1,
}

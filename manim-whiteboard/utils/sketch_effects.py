"""
Sketch-style visual effects for Manim.
Creates hand-drawn appearance for shapes and lines.
"""

from manim import *
import numpy as np
from typing import List, Tuple


def add_noise_to_path(points: np.ndarray, roughness: float = 0.05) -> np.ndarray:
    """
    Add random noise to path points to simulate hand-drawn effect.

    Args:
        points: Original path points
        roughness: Amount of randomness (0.0 to 0.2 recommended)

    Returns:
        Modified points with noise added
    """
    if roughness == 0:
        return points

    noise = np.random.normal(0, roughness, points.shape)
    # Don't add noise to z-coordinate
    noise[:, 2] = 0
    return points + noise


class SketchyPolygon(Polygon):
    """
    A polygon that looks hand-drawn with slight imperfections.
    """

    def __init__(
        self,
        *vertices,
        roughness: float = 0.03,
        stroke_variation: bool = True,
        **kwargs
    ):
        # Set default whiteboard style
        kwargs.setdefault('color', BLACK)
        kwargs.setdefault('stroke_width', 4)
        kwargs.setdefault('fill_opacity', 0)

        super().__init__(*vertices, **kwargs)

        # Apply roughness
        if roughness > 0:
            self._apply_sketch_effect(roughness)

    def _apply_sketch_effect(self, roughness: float):
        """Apply hand-drawn effect to the polygon."""
        points = self.get_points()
        if len(points) > 0:
            noisy_points = add_noise_to_path(points, roughness)
            self.set_points(noisy_points)


class HandDrawnLine(Line):
    """
    A line that appears to be drawn by hand.
    """

    def __init__(
        self,
        start: np.ndarray,
        end: np.ndarray,
        roughness: float = 0.02,
        **kwargs
    ):
        kwargs.setdefault('color', BLACK)
        kwargs.setdefault('stroke_width', 3)

        super().__init__(start, end, **kwargs)

        if roughness > 0:
            self._add_wobble(roughness)

    def _add_wobble(self, roughness: float):
        """Add slight wobble to simulate hand drawing."""
        points = self.get_points()
        if len(points) > 0:
            noisy_points = add_noise_to_path(points, roughness)
            self.set_points(noisy_points)


class SketchyRectangle(Rectangle):
    """
    A rectangle with hand-drawn appearance.
    """

    def __init__(
        self,
        width: float = 4.0,
        height: float = 2.0,
        roughness: float = 0.02,
        **kwargs
    ):
        kwargs.setdefault('color', BLACK)
        kwargs.setdefault('stroke_width', 3)

        super().__init__(width=width, height=height, **kwargs)

        if roughness > 0:
            points = self.get_points()
            if len(points) > 0:
                noisy_points = add_noise_to_path(points, roughness)
                self.set_points(noisy_points)


class SketchyCircle(Circle):
    """
    A circle with hand-drawn appearance (slightly imperfect).
    """

    def __init__(
        self,
        radius: float = 1.0,
        roughness: float = 0.02,
        **kwargs
    ):
        kwargs.setdefault('color', BLACK)
        kwargs.setdefault('stroke_width', 3)

        super().__init__(radius=radius, **kwargs)

        if roughness > 0:
            points = self.get_points()
            if len(points) > 0:
                noisy_points = add_noise_to_path(points, roughness)
                self.set_points(noisy_points)


class MarkerText(Text):
    """
    Text styled to look like whiteboard marker writing.
    """

    def __init__(
        self,
        text: str,
        font_size: float = 36,
        **kwargs
    ):
        kwargs.setdefault('color', BLACK)
        kwargs.setdefault('font', 'Sans')
        kwargs.setdefault('weight', BOLD)

        super().__init__(text, font_size=font_size, **kwargs)


class ArabicText(Text):
    """
    Arabic text with proper RTL rendering.
    Note: Requires Arabic font installed on system.
    """

    def __init__(
        self,
        text: str,
        font_size: float = 36,
        **kwargs
    ):
        kwargs.setdefault('color', BLACK)
        # Common Arabic fonts - adjust based on your system
        kwargs.setdefault('font', 'Noto Sans Arabic')

        super().__init__(text, font_size=font_size, **kwargs)


def create_drawing_animation(
    mobject: Mobject,
    run_time: float = 2.0,
    lag_ratio: float = 0.1
) -> Animation:
    """
    Create a drawing animation that mimics hand-drawing.

    Args:
        mobject: The object to animate
        run_time: Duration of animation
        lag_ratio: Stagger effect for complex shapes

    Returns:
        Animation object
    """
    return Create(
        mobject,
        run_time=run_time,
        lag_ratio=lag_ratio,
        rate_func=rate_functions.ease_in_out_sine
    )


def create_writing_animation(
    text_mobject: Text,
    run_time: float = 1.5
) -> Animation:
    """
    Create a writing animation for text.

    Args:
        text_mobject: The text to animate
        run_time: Duration of animation

    Returns:
        Animation object
    """
    return Write(
        text_mobject,
        run_time=run_time,
        rate_func=rate_functions.ease_in_out_sine
    )

#!/usr/bin/env python3
"""
Custom Whiteboard Template
==========================

A reusable template for creating whiteboard-style animations.
Copy this file and modify for your own content.

Usage:
    manim -pql scenes/custom_template.py WhiteboardTemplate
"""

from manim import *
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.colors import WHITEBOARD_COLORS
from utils.sketch_effects import SketchyPolygon, SketchyRectangle, MarkerText


class WhiteboardTemplate(Scene):
    """
    Template for whiteboard-style animations.
    Customize the methods below for your content.
    """

    def construct(self):
        # Setup
        self.setup_whiteboard()

        # Your animation sequence
        self.intro_animation()
        self.main_content()
        self.outro_animation()

    def setup_whiteboard(self):
        """Configure the whiteboard appearance."""
        # White background
        self.camera.background_color = WHITEBOARD_COLORS['background']

        # Optional: Add subtle paper texture effect
        # self.add_paper_texture()

    def intro_animation(self):
        """Opening animation - customize this."""
        title = Text(
            "Your Title Here",
            font_size=48,
            color=WHITEBOARD_COLORS['marker_black'],
            weight=BOLD
        ).to_edge(UP)

        self.play(Write(title), run_time=2)
        self.wait(1)

    def main_content(self):
        """Main content - customize this."""
        # Example: Draw a shape
        shape = SketchyRectangle(
            width=4,
            height=3,
            color=WHITEBOARD_COLORS['marker_blue'],
            stroke_width=4
        )

        label = Text(
            "Main Content",
            font_size=24,
            color=WHITEBOARD_COLORS['text_primary']
        ).move_to(shape.get_center())

        self.play(Create(shape), run_time=2)
        self.play(Write(label), run_time=1)
        self.wait(2)

    def outro_animation(self):
        """Closing animation - customize this."""
        # Fade everything out
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )

        # Final message
        thanks = Text(
            "Thank you for watching!",
            font_size=36,
            color=WHITEBOARD_COLORS['marker_black']
        )

        self.play(Write(thanks), run_time=1.5)
        self.wait(2)


class BulletPointsScene(Scene):
    """
    Template for bullet point presentations.
    """

    def construct(self):
        self.camera.background_color = WHITE

        title = Text(
            "Key Points",
            font_size=42,
            color=BLACK,
            weight=BOLD
        ).to_edge(UP)

        self.play(Write(title))

        points = [
            "First important point",
            "Second key insight",
            "Third conclusion",
            "Final takeaway"
        ]

        bullet_group = VGroup()
        for i, point in enumerate(points):
            bullet = Text(
                f"  {point}",
                font_size=28,
                color=BLACK
            )
            bullet_group.add(bullet)

        bullet_group.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        bullet_group.next_to(title, DOWN, buff=1)

        for bullet in bullet_group:
            self.play(Write(bullet), run_time=1)
            self.wait(0.5)

        self.wait(2)


class ComparisonScene(Scene):
    """
    Template for side-by-side comparisons.
    """

    def construct(self):
        self.camera.background_color = WHITE

        # Left side
        left_title = Text("Before", font_size=32, color=BLUE).to_edge(UP).shift(LEFT * 3)
        left_box = Rectangle(width=3, height=4, color=BLUE).shift(LEFT * 3)

        # Right side
        right_title = Text("After", font_size=32, color=GREEN).to_edge(UP).shift(RIGHT * 3)
        right_box = Rectangle(width=3, height=4, color=GREEN).shift(RIGHT * 3)

        # VS indicator
        vs = Text("VS", font_size=48, color=RED, weight=BOLD)

        self.play(
            Write(left_title),
            Write(right_title),
            run_time=1
        )
        self.play(
            Create(left_box),
            Create(right_box),
            run_time=1.5
        )
        self.play(Write(vs), run_time=0.5)

        self.wait(3)

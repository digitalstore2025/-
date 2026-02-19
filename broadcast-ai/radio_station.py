"""
Quran-Conditioned Palestinian Broadcast AI — Radio Station

Audio-only radio broadcast mode with:
- Live RSS headlines
- Scheduled content blocks (news / radio / quran / podcast)
- Jingles and bumpers between segments
- Continuous WAV file generation for streaming
"""

import os
import random
import time
from pathlib import Path

import config
from generate import generate_voice
from logger import get_logger
from rss_feed import get_full_bulletin, get_unseen_headlines
from scheduler import get_current_block

log = get_logger("radio")

RADIO_OUTPUT = config.OUTPUT_DIR / "radio_live.wav"


def _pick_content(block_type: str) -> str:
    """Select text content based on the current schedule block."""

    if block_type == "news":
        bulletin = get_full_bulletin(max_items=3)
        if bulletin:
            return bulletin
        return random.choice(config.NEWS_HEADLINES)

    if block_type == "quran":
        return random.choice(config.QURAN_SEGMENTS)

    if block_type == "podcast":
        intro = random.choice(config.PODCAST_INTROS)
        headlines = get_unseen_headlines(2)
        if headlines:
            body = ". ".join(headlines)
            return f"{intro}. {body}. شكراً لاستماعكم."
        return intro

    if block_type == "authority":
        return random.choice(config.AUTHORITY_STATEMENTS)

    # Default: radio
    return random.choice(config.RADIO_INTROS)


def _generate_bumper() -> str | None:
    """Generate a short station ID bumper between segments."""

    bumpers = [
        "صوت القدس",
        "إذاعة صوت فلسطين",
        "أنتم على الهواء مع صوت القدس",
    ]
    text = random.choice(bumpers)

    try:
        return generate_voice(text, style="radio", output_name="bumper.wav")
    except Exception as exc:
        log.warning("Bumper generation failed: %s", exc)
        return None


def run_radio(with_bumpers: bool = True):
    """Infinite radio broadcast loop.

    Generates audio segments based on the current schedule block,
    inserts bumpers between segments, and writes to RADIO_OUTPUT.
    """

    log.info("=== Palestinian AI Radio Station — ON AIR ===")

    segment_count = 0

    while True:
        block_type = get_current_block()
        log.info("[Block: %s] Generating segment #%d", block_type, segment_count + 1)

        text = _pick_content(block_type)
        log.info("Text: %s", text[:80])

        try:
            path = generate_voice(
                text,
                style=block_type,
                output_name="radio_live.wav",
            )
            log.info("Segment ready: %s", path)
            segment_count += 1

            # Insert bumper every 3 segments
            if with_bumpers and segment_count % 3 == 0:
                _generate_bumper()

        except Exception as exc:
            log.error("Segment generation failed: %s", exc)

        time.sleep(config.BROADCAST_LOOP_PAUSE)


if __name__ == "__main__":
    run_radio()

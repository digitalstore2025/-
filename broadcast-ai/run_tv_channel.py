#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — TV Channel Loop

Full broadcast loop with:
- Schedule-aware content selection (news / radio / quran / podcast)
- Live RSS headline integration
- Lip-synced anchor video via Wav2Lip (with audio-only fallback)
- Segment history tracking
- Graceful shutdown
"""

import json
import os
import random
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import config
from generate import generate_voice
from logger import get_logger
from rss_feed import get_full_bulletin, get_unseen_headlines
from scheduler import get_current_block, get_next_block_change

log = get_logger("tv_channel")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_running = True
_segment_history: list[dict] = []

HISTORY_FILE = config.OUTPUT_DIR / "segment_history.json"
VIDEO_OUTPUT = str(config.OUTPUT_DIR / "tv_channel.mp4")
AUDIO_OUTPUT = str(config.OUTPUT_DIR / "tv_audio.wav")


def _signal_handler(signum, frame):
    global _running
    log.info("Shutdown signal received (signal %d)", signum)
    _running = False


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ---------------------------------------------------------------------------
# Content selection
# ---------------------------------------------------------------------------

def _pick_content(block_type: str) -> tuple[str, str]:
    """Select text and style based on the current schedule block.

    Returns (text, style) tuple.
    """

    if block_type == "news":
        # Try live RSS first
        bulletin = get_full_bulletin(max_items=3)
        if bulletin:
            return bulletin, "news"
        return random.choice(config.NEWS_HEADLINES), "news"

    if block_type == "quran":
        return random.choice(config.QURAN_SEGMENTS), "quran"

    if block_type == "podcast":
        intro = random.choice(config.PODCAST_INTROS)
        headlines = get_unseen_headlines(2)
        if headlines:
            body = ". ".join(headlines)
            return f"{intro}. {body}. شكراً لاستماعكم.", "podcast"
        return intro, "podcast"

    if block_type == "authority":
        return random.choice(config.AUTHORITY_STATEMENTS), "authority"

    # Default: radio
    return random.choice(config.RADIO_INTROS), "radio"


# ---------------------------------------------------------------------------
# Anchor video
# ---------------------------------------------------------------------------

def _ensure_anchor_video():
    """Create a static anchor video from an image if it doesn't exist yet."""

    anchor_vid = config.ANCHOR_VIDEO
    anchor_img = config.ANCHOR_IMAGE

    if anchor_vid.exists():
        return

    if not anchor_img.exists():
        log.warning("No anchor image at %s — video segments will be audio-only", anchor_img)
        return

    config.INPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(anchor_img),
                "-c:v", "libx264",
                "-t", "15",
                "-pix_fmt", "yuv420p",
                "-r", "25",
                str(anchor_vid),
            ],
            check=True,
            capture_output=True,
        )
        log.info("Created anchor video: %s", anchor_vid)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log.warning("Failed to create anchor video: %s", e)


# ---------------------------------------------------------------------------
# Segment generation
# ---------------------------------------------------------------------------

def _generate_segment(text: str, style: str) -> dict:
    """Produce one broadcast segment and return metadata dict."""

    t0 = time.time()

    # Generate audio
    audio_path = generate_voice(text, style=style, output_name="tv_audio.wav")

    result = {
        "timestamp": datetime.now().isoformat(),
        "text": text[:100],
        "style": style,
        "audio": audio_path,
        "video": None,
        "duration": 0,
    }

    # Attempt lip-sync video
    wav2lip_ok = (
        config.WAV2LIP_INFERENCE.exists()
        and config.WAV2LIP_CHECKPOINT.exists()
        and config.ANCHOR_VIDEO.exists()
    )

    if wav2lip_ok:
        try:
            subprocess.run(
                [
                    "python", str(config.WAV2LIP_INFERENCE),
                    "--checkpoint_path", str(config.WAV2LIP_CHECKPOINT),
                    "--face", str(config.ANCHOR_VIDEO),
                    "--audio", audio_path,
                    "--outfile", VIDEO_OUTPUT,
                ],
                check=True,
                capture_output=True,
            )
            result["video"] = VIDEO_OUTPUT
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            log.warning("Wav2Lip failed: %s — using audio only", exc)
    else:
        log.debug("Wav2Lip not available — audio only mode")

    result["duration"] = round(time.time() - t0, 1)
    return result


def _save_history():
    """Persist segment history to disk."""
    try:
        # Keep last 100 segments
        recent = _segment_history[-100:]
        HISTORY_FILE.write_text(
            json.dumps(recent, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main broadcast loop
# ---------------------------------------------------------------------------

def run():
    """Infinite broadcast loop with schedule-aware content selection."""

    _ensure_anchor_video()

    log.info("=" * 60)
    log.info("  Palestinian AI TV Channel — ON AIR")
    log.info("=" * 60)

    segment_count = 0

    while _running:
        block_type = get_current_block()
        next_info = get_next_block_change()

        text, style = _pick_content(block_type)

        log.info(
            "[#%d] Block: %s | Next change: %s in %dm",
            segment_count + 1,
            block_type,
            next_info.get("next_label", "?"),
            next_info.get("minutes_until", 0),
        )
        log.info("  Text: %s", text[:80])

        try:
            result = _generate_segment(text, style)
            _segment_history.append(result)
            _save_history()

            media_type = "VIDEO" if result["video"] else "AUDIO"
            log.info(
                "  [%s] Segment #%d ready (%.1fs)",
                media_type, segment_count + 1, result["duration"],
            )
            segment_count += 1

        except Exception as exc:
            log.error("  Segment generation failed: %s", exc)

        time.sleep(config.BROADCAST_LOOP_PAUSE)

    log.info("TV Channel stopped after %d segments", segment_count)


if __name__ == "__main__":
    run()

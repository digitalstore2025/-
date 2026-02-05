#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — TV Channel Loop

Continuously generates AI news segments:
  1. Picks a headline
  2. Synthesises speech with the broadcast voice model
  3. Produces a lip-synced anchor video (Wav2Lip)
  4. Writes the result to  output/tv_channel.mp4  for the streaming server
"""

import os
import random
import subprocess
import time

from generate import generate_voice

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANCHOR_VIDEO = "input/anchor.mp4"
VIDEO_OUTPUT = "output/tv_channel.mp4"

WAV2LIP_INFERENCE = "Wav2Lip/inference.py"
WAV2LIP_CHECKPOINT = "models/wav2lip.pth"

# Headline pool — extend or replace with a live RSS feed
NEWS_HEADLINES = [
    "هنا غزة من إذاعة صوت القدس",
    "نوافيكم بآخر الأخبار من فلسطين",
    "تواصل الجهات المختصة متابعة الأوضاع الميدانية",
    "نبقى معكم في متابعة مستمرة على مدار الساعة",
    "بسم الله الرحمن الرحيم، نقدم لكم النشرة الإخبارية",
    "آخر المستجدات من الميدان الفلسطيني",
    "صوت فلسطين يوافيكم بالتطورات الأخيرة",
    "أهلاً بكم في نشرة أخبار صوت القدس",
]

LOOP_PAUSE_SECONDS = 5

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_anchor_video():
    """Create a static anchor video from an image if it doesn't exist yet."""
    if os.path.exists(ANCHOR_VIDEO):
        return

    anchor_img = "input/anchor.jpg"
    if not os.path.exists(anchor_img):
        print(f"[ERROR] Place an anchor image at {anchor_img}")
        return

    os.makedirs("input", exist_ok=True)
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", anchor_img,
                "-c:v", "libx264",
                "-t", "15",
                "-pix_fmt", "yuv420p",
                ANCHOR_VIDEO,
            ],
            check=True,
            capture_output=True,
        )
        print(f"[ANCHOR] Created {ANCHOR_VIDEO}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create anchor video: {e}")
    except FileNotFoundError:
        print(f"[ERROR] ffmpeg not found - cannot create anchor video")


def _generate_segment(headline: str) -> str | None:
    """Produce one lip-synced news segment and return the output path."""

    audio_path = generate_voice(headline, style="news", output_name="tv_audio.wav")

    if not os.path.exists(WAV2LIP_INFERENCE):
        print("[WARN] Wav2Lip not found — skipping lip-sync, using audio only")
        return audio_path

    if not os.path.exists(WAV2LIP_CHECKPOINT):
        print("[WARN] Wav2Lip checkpoint not found — skipping lip-sync")
        return audio_path

    try:
        subprocess.run(
            [
                "python", WAV2LIP_INFERENCE,
                "--checkpoint_path", WAV2LIP_CHECKPOINT,
                "--face", ANCHOR_VIDEO,
                "--audio", audio_path,
                "--outfile", VIDEO_OUTPUT,
            ],
            check=True,
        )
        return VIDEO_OUTPUT
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Wav2Lip processing failed: {e}")
        print(f"[WARN] Falling back to audio only")
        return audio_path
    except FileNotFoundError:
        print(f"[WARN] Python interpreter or Wav2Lip script not found")
        print(f"[WARN] Falling back to audio only")
        return audio_path


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run():
    """Infinite broadcast loop."""

    _ensure_anchor_video()

    print("[TV] Palestinian AI Broadcast Channel — starting loop")

    while True:
        headline = random.choice(NEWS_HEADLINES)
        print(f"[TV] >>> {headline}")

        try:
            result = _generate_segment(headline)
            if result:
                print(f"[TV] Segment ready: {result}")
        except KeyboardInterrupt:
            print("[TV] Shutting down broadcast loop")
            break
        except Exception as exc:
            print(f"[TV] Unexpected error during segment generation ({type(exc).__name__}): {exc}")
            print("[TV] Continuing to next segment...")

        time.sleep(LOOP_PAUSE_SECONDS)


if __name__ == "__main__":
    run()

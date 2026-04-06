"""
Quran-Conditioned Palestinian Broadcast AI — Podcast Generator

Creates self-contained podcast episodes by:
1. Fetching latest news from RSS feeds
2. Building an intro → body → outro script
3. Synthesising each segment
4. Concatenating into a single episode file
"""

import os
import subprocess
import time
from pathlib import Path

import config
from generate import generate_voice
from logger import get_logger
from rss_feed import get_unseen_headlines

log = get_logger("podcast")

EPISODES_DIR = config.OUTPUT_DIR / "episodes"
EPISODES_DIR.mkdir(parents=True, exist_ok=True)


def _concat_wavs(wav_paths: list[str], output: str):
    """Concatenate multiple WAV files using ffmpeg."""

    list_file = config.OUTPUT_DIR / "concat_list.txt"

    with open(list_file, "w", encoding="utf-8") as fh:
        for p in wav_paths:
            fh.write(f"file '{os.path.abspath(p)}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            output,
        ],
        check=True,
        capture_output=True,
    )

    list_file.unlink(missing_ok=True)


def generate_episode(
    topic: str = "",
    max_headlines: int = 5,
    episode_id: str = "",
) -> str:
    """Generate a complete podcast episode and return its file path.

    Parameters
    ----------
    topic:
        Optional topic override. If empty, uses RSS headlines.
    max_headlines:
        Number of headlines to include.
    episode_id:
        Identifier for the episode file. Auto-generated if empty.
    """

    if not episode_id:
        episode_id = time.strftime("%Y%m%d_%H%M%S")

    episode_path = str(EPISODES_DIR / f"episode_{episode_id}.wav")
    parts: list[str] = []

    log.info("=== Generating Episode: %s ===", episode_id)

    # --- Intro ---
    intro_text = (
        "بسم الله الرحمن الرحيم. "
        "أهلاً وسهلاً بكم في بودكاست صوت القدس. "
        "معكم في حلقة جديدة نستعرض فيها أهم الأخبار والمستجدات."
    )
    intro_wav = generate_voice(intro_text, style="podcast", output_name="ep_intro.wav")
    parts.append(intro_wav)
    log.info("Intro generated")

    # --- Body: headlines ---
    if topic:
        headlines = [topic]
    else:
        headlines = get_unseen_headlines(max_headlines)
        if not headlines:
            headlines = config.NEWS_HEADLINES[:max_headlines]

    for i, headline in enumerate(headlines, 1):
        body_text = f"الخبر رقم {i}. {headline}."
        wav = generate_voice(
            body_text,
            style="podcast",
            output_name=f"ep_body_{i}.wav",
        )
        parts.append(wav)
        log.info("Body segment %d/%d generated", i, len(headlines))

    # --- Outro ---
    outro_text = (
        "كانت هذه أبرز العناوين لهذا اليوم. "
        "شكراً لاستماعكم. نلتقيكم في الحلقة القادمة بإذن الله. "
        "دمتم بخير. السلام عليكم ورحمة الله وبركاته."
    )
    outro_wav = generate_voice(outro_text, style="podcast", output_name="ep_outro.wav")
    parts.append(outro_wav)
    log.info("Outro generated")

    # --- Concatenate ---
    _concat_wavs(parts, episode_path)
    log.info("=== Episode saved: %s ===", episode_path)

    return episode_path


if __name__ == "__main__":
    path = generate_episode()
    print(f"Episode: {path}")

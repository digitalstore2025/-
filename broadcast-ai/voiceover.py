"""
Quran-Conditioned Palestinian Broadcast AI — Voiceover Engine

Generates professional voiceovers for:
- Documentary narration
- Promotional spots
- Public service announcements
- Custom text input

Supports batch processing from a text file.
"""

import os
import subprocess
from pathlib import Path

import config
from generate import generate_voice
from logger import get_logger

log = get_logger("voiceover")

VOICEOVER_DIR = config.OUTPUT_DIR / "voiceovers"
VOICEOVER_DIR.mkdir(parents=True, exist_ok=True)


def generate_voiceover(
    text: str,
    output_name: str = "voiceover.wav",
    style: str = "voiceover",
    add_padding: bool = True,
    padding_seconds: float = 0.5,
) -> str:
    """Generate a single voiceover clip.

    Parameters
    ----------
    text:
        Arabic text to synthesise.
    output_name:
        Output filename inside the voiceovers directory.
    style:
        Voice style (voiceover, news, authority, quran).
    add_padding:
        If True, add silence padding at start/end.
    padding_seconds:
        Duration of silence padding.
    """

    raw_path = generate_voice(text, style=style, output_name=f"vo_raw_{output_name}")
    final_path = str(VOICEOVER_DIR / output_name)

    if add_padding:
        af = (
            f"adelay={int(padding_seconds * 1000)}|{int(padding_seconds * 1000)},"
            f"apad=pad_dur={padding_seconds}"
        )
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-af", af,
                final_path,
            ],
            check=True,
            capture_output=True,
        )
    else:
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw_path, "-c", "copy", final_path],
            check=True,
            capture_output=True,
        )

    log.info("Voiceover saved: %s", final_path)
    return final_path


def batch_voiceover(input_file: str, style: str = "voiceover") -> list[str]:
    """Process a text file where each line becomes a separate voiceover clip.

    Parameters
    ----------
    input_file:
        Path to a UTF-8 text file, one segment per line.
    style:
        Voice style to apply.

    Returns
    -------
    List of generated file paths.
    """

    paths: list[str] = []

    with open(input_file, encoding="utf-8") as fh:
        lines = [l.strip() for l in fh if l.strip()]

    log.info("Batch voiceover: %d segments from %s", len(lines), input_file)

    for i, line in enumerate(lines, 1):
        name = f"batch_{i:03d}.wav"
        path = generate_voiceover(line, output_name=name, style=style)
        paths.append(path)
        log.info("Batch %d/%d done", i, len(lines))

    return paths


def generate_promo(text: str, output_name: str = "promo.wav") -> str:
    """Generate a promotional spot with authority tone."""
    return generate_voiceover(text, output_name=output_name, style="authority")


def generate_psa(text: str, output_name: str = "psa.wav") -> str:
    """Generate a public service announcement."""
    return generate_voiceover(text, output_name=output_name, style="news")


if __name__ == "__main__":
    sample = "صوت القدس. صوت الحقيقة من فلسطين."
    path = generate_voiceover(sample)
    print(f"Voiceover: {path}")

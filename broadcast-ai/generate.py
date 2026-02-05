#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Voice Generator

Generates broadcast-grade Arabic speech from text using the fine-tuned model.
Applies professional audio post-processing (EQ, loudness normalisation).
"""

import os
import subprocess
import sys

from TTS.api import TTS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_PATH = "models/final_broadcast_model"
REFERENCE_WAV = "dataset_speaker/wavs/0001.wav"
OUTPUT_DIR = "output"

# ---------------------------------------------------------------------------
# Lazy-loaded TTS instance
# ---------------------------------------------------------------------------

_tts_instance: TTS | None = None


def _get_tts() -> TTS:
    global _tts_instance
    if _tts_instance is None:
        if not os.path.exists(MODEL_PATH):
            print(f"[ERROR] Model not found at {MODEL_PATH}")
            print("        Run  python train.py  first.")
            sys.exit(1)
        _tts_instance = TTS(MODEL_PATH)
    return _tts_instance


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_voice(
    text: str,
    style: str = "news",
    output_name: str = "news.wav",
) -> str:
    """Synthesise *text* and return the path to the processed WAV file.

    Parameters
    ----------
    text:
        Arabic text to synthesise.
    style:
        Label hint (currently unused by the model but reserved for future
        multi-style conditioning).
    output_name:
        Filename for the final output inside ``output/``.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_path = os.path.join(OUTPUT_DIR, "raw.wav")
    final_path = os.path.join(OUTPUT_DIR, output_name)

    tts = _get_tts()

    # --- Synthesise raw audio ------------------------------------------------
    tts.tts_to_file(
        text=text,
        speaker_wav=REFERENCE_WAV,
        language="ar",
        file_path=raw_path,
    )

    # --- Broadcast-grade post-processing via ffmpeg --------------------------
    #   highpass  80 Hz  — removes rumble / DC offset
    #   lowpass  8000 Hz — removes hiss above speech band
    #   loudnorm         — EBU R128 loudness normalisation (-16 LUFS)
    af_chain = (
        "highpass=f=80,"
        "lowpass=f=8000,"
        "loudnorm=I=-16:LRA=11:TP=-1.5"
    )

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", raw_path,
                "-af", af_chain,
                final_path,
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[WARN] ffmpeg post-processing failed: {e}")
        print(f"[WARN] Using raw audio output instead")
        # If ffmpeg fails, use the raw audio file
        final_path = raw_path
    except FileNotFoundError:
        print(f"[WARN] ffmpeg not found - skipping audio post-processing")
        print(f"[WARN] Using raw audio output instead")
        # If ffmpeg is not installed, use the raw audio file
        final_path = raw_path

    print(f"[GEN] {style} → {final_path}")
    return final_path


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_text = "هنا غزة، من إذاعة صوت القدس. نوافيكم بآخر الأخبار."
    path = generate_voice(sample_text, style="news", output_name="demo.wav")
    print(f"[DONE] {path}")

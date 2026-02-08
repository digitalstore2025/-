#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Voice Generator

Generates broadcast-grade Arabic speech from text using the fine-tuned model.
Supports multiple voice styles with per-style EQ, caching, input validation,
and retry logic.
"""

import hashlib
import os
import re
import subprocess
import sys
import time

from TTS.api import TTS

import config
from logger import get_logger

log = get_logger("generate")

# ---------------------------------------------------------------------------
# Lazy-loaded TTS instance
# ---------------------------------------------------------------------------

_tts_instance: TTS | None = None


def _get_tts() -> TTS:
    global _tts_instance
    if _tts_instance is None:
        if not config.MODEL_PATH.exists():
            log.error("Model not found at %s — run train.py first", config.MODEL_PATH)
            sys.exit(1)
        log.info("Loading TTS model from %s ...", config.MODEL_PATH)
        t0 = time.time()
        _tts_instance = TTS(str(config.MODEL_PATH))
        log.info("Model loaded in %.1fs", time.time() - t0)
    return _tts_instance


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_MAX_TEXT_LEN = 2000
_MIN_TEXT_LEN = 2


def _validate_text(text: str) -> str:
    """Sanitise and validate input text."""

    text = text.strip()

    if len(text) < _MIN_TEXT_LEN:
        raise ValueError(f"Text too short ({len(text)} chars, min {_MIN_TEXT_LEN})")

    if len(text) > _MAX_TEXT_LEN:
        log.warning("Text truncated from %d to %d chars", len(text), _MAX_TEXT_LEN)
        text = text[:_MAX_TEXT_LEN]

    # Strip control characters (keep Arabic, punctuation, whitespace)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text


# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------

def _cache_key(text: str, style: str) -> str:
    """Deterministic cache key from text + style."""
    raw = f"{style}::{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _get_cached(text: str, style: str) -> str | None:
    """Return cached WAV path if it exists."""
    key = _cache_key(text, style)
    cached = config.CACHE_DIR / f"{key}.wav"
    if cached.exists():
        log.debug("Cache HIT: %s", key)
        return str(cached)
    return None


def _save_cache(text: str, style: str, wav_path: str):
    """Copy generated WAV into the cache."""
    key = _cache_key(text, style)
    dst = config.CACHE_DIR / f"{key}.wav"
    try:
        subprocess.run(
            ["cp", wav_path, str(dst)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        pass


# ---------------------------------------------------------------------------
# Post-processing
# ---------------------------------------------------------------------------

def _postprocess(raw_path: str, final_path: str, style: str):
    """Apply broadcast-grade audio EQ via ffmpeg."""

    af_chain = config.STYLE_EQ.get(style, config.FFMPEG_AF_CHAIN)

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
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        error_type = "not found" if isinstance(e, FileNotFoundError) else "failed"
        print(f"[WARN] ffmpeg {error_type} - skipping audio post-processing")
        print(f"[WARN] Using raw audio output instead")
        # If ffmpeg fails or is not installed, use the raw audio file
        final_path = raw_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_voice(
    text: str,
    style: str = "news",
    output_name: str = "news.wav",
    use_cache: bool = True,
    retries: int = 2,
) -> str:
    """Synthesise *text* and return the path to the processed WAV file.

    Parameters
    ----------
    text:
        Arabic text to synthesise.
    style:
        Voice style — determines which EQ preset to apply.
        Options: news, radio, podcast, voiceover, authority, quran.
    output_name:
        Filename for the final output inside ``output/``.
    use_cache:
        If True, reuse previously generated audio for identical text+style.
    retries:
        Number of retry attempts on synthesis failure.
    """

    text = _validate_text(text)

    # Check cache
    if use_cache:
        cached = _get_cached(text, style)
        if cached:
            final_path = str(config.OUTPUT_DIR / output_name)
            subprocess.run(
                ["cp", cached, final_path],
                check=True,
                capture_output=True,
            )
            log.info("[CACHE] %s -> %s", style, final_path)
            return final_path

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_path = str(config.OUTPUT_DIR / "raw.wav")
    final_path = str(config.OUTPUT_DIR / output_name)

    # Synthesise with retry
    last_error = None
    for attempt in range(1, retries + 2):
        try:
            tts = _get_tts()

            ref_wav = str(config.REFERENCE_WAV)
            if not os.path.exists(ref_wav):
                log.warning("Reference WAV not found at %s, using model default", ref_wav)
                ref_wav = None

            t0 = time.time()

            if ref_wav:
                tts.tts_to_file(
                    text=text,
                    speaker_wav=ref_wav,
                    language=config.LANGUAGE,
                    file_path=raw_path,
                )
            else:
                tts.tts_to_file(
                    text=text,
                    language=config.LANGUAGE,
                    file_path=raw_path,
                )

            synth_time = time.time() - t0
            log.info("Synthesis took %.1fs (attempt %d)", synth_time, attempt)
            last_error = None
            break

        except Exception as exc:
            last_error = exc
            log.warning("Synthesis attempt %d/%d failed: %s", attempt, retries + 1, exc)
            if attempt <= retries:
                time.sleep(1)

    if last_error:
        raise RuntimeError(f"Synthesis failed after {retries + 1} attempts: {last_error}")

    # Post-process
    _postprocess(raw_path, final_path, style)

    # Save to cache
    if use_cache:
        _save_cache(text, style, final_path)

    log.info("[GEN] %s -> %s", style, final_path)
    return final_path


def get_available_styles() -> list[str]:
    """Return list of available voice styles."""
    return list(config.STYLE_EQ.keys())


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Palestinian AI Voice Generator")
    parser.add_argument("--text", default="هنا غزة، من إذاعة صوت القدس. نوافيكم بآخر الأخبار.")
    parser.add_argument("--style", default="news", choices=get_available_styles())
    parser.add_argument("--output", default="demo.wav")
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    path = generate_voice(
        args.text,
        style=args.style,
        output_name=args.output,
        use_cache=not args.no_cache,
    )
    print(f"Output: {path}")

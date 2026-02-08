#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Demo Mode

Runs the full broadcast system using the pre-trained XTTS v2 model
WITHOUT requiring fine-tuning or custom datasets.

This lets you test the entire pipeline immediately:
  python demo.py              — Generate demo audio + start server
  python demo.py --generate   — Generate sample audio only
  python demo.py --server     — Start web server only
"""

import argparse
import multiprocessing
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import config
from logger import get_logger

log = get_logger("demo")

DEMO_OUTPUT = config.OUTPUT_DIR
DEMO_TEXTS = {
    "news": [
        "بسم الله الرحمن الرحيم. نقدم لكم النشرة الإخبارية من إذاعة صوت القدس.",
        "هنا غزة. نوافيكم بآخر الأخبار والمستجدات من الميدان الفلسطيني.",
        "أهلاً بكم في نشرة أخبار صوت القدس. نبقى معكم في متابعة مستمرة.",
    ],
    "radio": [
        "أهلاً وسهلاً بكم في إذاعة صوت القدس. معكم من استوديوهات صوت فلسطين.",
        "طابت أوقاتكم مستمعينا الكرام. نحييكم من أرض فلسطين الحبيبة.",
    ],
    "quran": [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    ],
}

_processes = []


def _shutdown(signum=None, frame=None):
    for p in _processes:
        if p.is_alive():
            p.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


def _check_tts():
    """Check if TTS is available."""
    try:
        from TTS.api import TTS
        return True
    except ImportError:
        log.error("TTS package not installed. Run: pip3 install TTS==0.22.0")
        return False


def _generate_demo_audio():
    """Generate demo audio files using pre-trained XTTS v2."""

    from TTS.api import TTS

    DEMO_OUTPUT.mkdir(parents=True, exist_ok=True)

    log.info("Loading pre-trained XTTS v2 model (first time will download ~2GB)...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    log.info("Model loaded successfully!")

    # Check for reference audio
    ref_wav = str(config.REFERENCE_WAV)
    has_ref = os.path.exists(ref_wav)

    if not has_ref:
        log.info("No reference WAV found. Generating with default voice.")
        log.info("For voice cloning, place a WAV file at: %s", ref_wav)

    generated = []

    for style, texts in DEMO_TEXTS.items():
        for i, text in enumerate(texts):
            output_name = f"demo_{style}_{i + 1}.wav"
            raw_path = str(DEMO_OUTPUT / f"raw_{output_name}")
            final_path = str(DEMO_OUTPUT / output_name)

            log.info("[%s] Generating: %s...", style, text[:50])

            try:
                if has_ref:
                    tts.tts_to_file(
                        text=text,
                        speaker_wav=ref_wav,
                        language="ar",
                        file_path=raw_path,
                    )
                else:
                    tts.tts_to_file(
                        text=text,
                        language="ar",
                        file_path=raw_path,
                    )

                # Apply EQ
                af_chain = config.STYLE_EQ.get(style, config.FFMPEG_AF_CHAIN)
                subprocess.run(
                    ["ffmpeg", "-y", "-i", raw_path, "-af", af_chain, final_path],
                    check=True,
                    capture_output=True,
                )

                generated.append(final_path)
                log.info("  -> %s", final_path)

                # Remove raw file
                Path(raw_path).unlink(missing_ok=True)

            except Exception as exc:
                log.error("  Generation failed: %s", exc)

    # Create the tv_audio.wav for the server (use first news clip)
    if generated:
        first = generated[0]
        tv_audio = str(DEMO_OUTPUT / "tv_audio.wav")
        subprocess.run(
            ["cp", first, tv_audio],
            capture_output=True,
        )
        log.info("Set %s as live stream audio", tv_audio)

    log.info("Generated %d demo clips in %s", len(generated), DEMO_OUTPUT)
    return generated


def _run_demo_server():
    """Start the web server."""
    from tv_server import app
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False)


def _run_demo_loop():
    """Simple demo broadcast loop that cycles through generated clips."""

    import random

    log.info("Demo broadcast loop started")

    while True:
        clips = list(DEMO_OUTPUT.glob("demo_*.wav"))
        if not clips:
            time.sleep(5)
            continue

        clip = random.choice(clips)
        tv_audio = DEMO_OUTPUT / "tv_audio.wav"
        subprocess.run(["cp", str(clip), str(tv_audio)], capture_output=True)

        log.info("[DEMO] Now playing: %s", clip.name)
        time.sleep(config.BROADCAST_LOOP_PAUSE)


def main():
    parser = argparse.ArgumentParser(
        description="Palestinian AI Broadcast — Demo Mode (no training required)"
    )
    parser.add_argument("--generate", action="store_true", help="Generate demo audio only")
    parser.add_argument("--server", action="store_true", help="Start server only (assumes audio exists)")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("  Palestinian AI Broadcast — DEMO MODE")
    log.info("  Using pre-trained XTTS v2 (no fine-tuning)")
    log.info("=" * 60)

    if args.server:
        log.info("Starting web server at http://localhost:%d", config.SERVER_PORT)
        _run_demo_server()
        return

    if not _check_tts():
        sys.exit(1)

    # Generate demo audio
    generated = _generate_demo_audio()

    if args.generate:
        log.info("Demo audio generation complete. Files in: %s", DEMO_OUTPUT)
        return

    if not generated:
        log.error("No audio generated. Check TTS installation.")
        sys.exit(1)

    # Start server + demo loop
    log.info("")
    log.info("Starting demo broadcast...")

    p_server = multiprocessing.Process(target=_run_demo_server, daemon=True)
    p_loop = multiprocessing.Process(target=_run_demo_loop, daemon=True)

    _processes.extend([p_server, p_loop])

    p_server.start()
    p_loop.start()

    log.info("  Web UI: http://localhost:%d", config.SERVER_PORT)
    log.info("  Press Ctrl+C to stop")
    log.info("=" * 60)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()

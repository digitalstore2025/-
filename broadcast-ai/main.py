#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Unified Launcher

Starts all broadcast services from a single command:
  python main.py             — Start TV channel + web server
  python main.py --radio     — Start radio station + web server
  python main.py --all       — Start TV + radio + web server
  python main.py --server    — Start web server only
  python main.py --podcast   — Generate a podcast episode and exit
  python main.py --voiceover — Run voiceover from text file
"""

import argparse
import multiprocessing
import os
import signal
import sys
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import config
from logger import get_logger

log = get_logger("main")

_processes: list[multiprocessing.Process] = []


def _shutdown(signum=None, frame=None):
    log.info("Shutting down all services...")
    for p in _processes:
        if p.is_alive():
            p.terminate()
    for p in _processes:
        p.join(timeout=5)
    log.info("All services stopped.")
    sys.exit(0)


signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)


# ---------------------------------------------------------------------------
# Service runners
# ---------------------------------------------------------------------------

def _run_tv():
    from run_tv_channel import run
    run()


def _run_radio():
    from radio_station import run_radio
    run_radio()


def _run_server():
    from tv_server import app
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False)


def _run_podcast(topic: str = ""):
    from podcast_generator import generate_episode
    path = generate_episode(topic=topic)
    log.info("Podcast episode: %s", path)


def _run_voiceover(input_file: str, style: str):
    from voiceover import batch_voiceover
    paths = batch_voiceover(input_file, style=style)
    log.info("Generated %d voiceover clips", len(paths))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Palestinian AI Broadcast — Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Start TV channel + web server
  python main.py --radio      Start radio + web server
  python main.py --all        Start TV + radio + web server
  python main.py --server     Web server only
  python main.py --podcast    Generate a podcast episode
  python main.py --voiceover script.txt
        """,
    )

    parser.add_argument("--all", action="store_true", help="Start all services (TV + radio + server)")
    parser.add_argument("--tv", action="store_true", help="Start TV channel (default)")
    parser.add_argument("--radio", action="store_true", help="Start radio station")
    parser.add_argument("--server", action="store_true", help="Start web server only")
    parser.add_argument("--podcast", nargs="?", const="", metavar="TOPIC", help="Generate podcast episode")
    parser.add_argument("--voiceover", metavar="FILE", help="Generate voiceover from text file")
    parser.add_argument("--style", default="voiceover", help="Voice style for voiceover")

    args = parser.parse_args()

    log.info("=" * 60)
    log.info("  Palestinian AI Broadcast System")
    log.info("  Quran-Conditioned Voice Model")
    log.info("=" * 60)

    # --- One-shot modes ---
    if args.podcast is not None:
        _run_podcast(args.podcast)
        return

    if args.voiceover:
        _run_voiceover(args.voiceover, args.style)
        return

    # --- Service modes ---
    if args.server:
        log.info("Starting web server only on port %d", config.SERVER_PORT)
        _run_server()
        return

    # Determine which services to start
    run_tv = args.all or args.tv or (not args.radio and not args.server)
    run_radio = args.all or args.radio

    if run_tv:
        p = multiprocessing.Process(target=_run_tv, name="tv-channel", daemon=True)
        _processes.append(p)
        log.info("  [+] TV Channel")

    if run_radio:
        p = multiprocessing.Process(target=_run_radio, name="radio-station", daemon=True)
        _processes.append(p)
        log.info("  [+] Radio Station")

    # Always start the web server
    p = multiprocessing.Process(target=_run_server, name="web-server", daemon=True)
    _processes.append(p)
    log.info("  [+] Web Server (port %d)", config.SERVER_PORT)

    # Start all
    for p in _processes:
        p.start()
        log.info("  Started: %s (PID %d)", p.name, p.pid)

    log.info("")
    log.info("  All services running. Press Ctrl+C to stop.")
    log.info("  Web UI: http://localhost:%d", config.SERVER_PORT)
    log.info("=" * 60)

    # Monitor processes
    try:
        while True:
            for p in _processes:
                if not p.is_alive():
                    log.warning("Service %s (PID %d) died — restarting...", p.name, p.pid)

                    if p.name == "tv-channel":
                        new_p = multiprocessing.Process(target=_run_tv, name="tv-channel", daemon=True)
                    elif p.name == "radio-station":
                        new_p = multiprocessing.Process(target=_run_radio, name="radio-station", daemon=True)
                    else:
                        new_p = multiprocessing.Process(target=_run_server, name="web-server", daemon=True)

                    _processes.remove(p)
                    _processes.append(new_p)
                    new_p.start()
                    log.info("  Restarted: %s (PID %d)", new_p.name, new_p.pid)

            time.sleep(5)
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()

"""
Quran-Conditioned Palestinian Broadcast AI — Broadcast Scheduler

Time-based scheduling for broadcast content blocks.
Maps time ranges to content types (news, radio, quran, podcast, etc.).
"""

from datetime import datetime

import config
from logger import get_logger

log = get_logger("scheduler")


def _parse_time(t: str) -> tuple[int, int]:
    """Parse 'HH:MM' to (hour, minute)."""
    parts = t.split(":")
    return int(parts[0]), int(parts[1])


def _minutes_since_midnight(h: int, m: int) -> int:
    return h * 60 + m


def get_current_block() -> str:
    """Return the content type for the current time of day.

    Uses ``config.SCHEDULE_BLOCKS`` mapping of ``"HH:MM-HH:MM": "type"``.
    Falls back to ``"radio"`` if no block matches.
    """

    now = datetime.now()
    now_mins = _minutes_since_midnight(now.hour, now.minute)

    for time_range, block_type in config.SCHEDULE_BLOCKS.items():
        start_str, end_str = time_range.split("-")
        sh, sm = _parse_time(start_str)
        eh, em = _parse_time(end_str)

        start_mins = _minutes_since_midnight(sh, sm)
        end_mins = _minutes_since_midnight(eh, em)

        # Handle midnight crossing
        if end_mins <= start_mins:
            if now_mins >= start_mins or now_mins < end_mins:
                return block_type
        else:
            if start_mins <= now_mins < end_mins:
                return block_type

    return "radio"


def get_schedule_display() -> list[dict]:
    """Return the full schedule as a list for display in the web UI."""

    schedule = []
    for time_range, block_type in config.SCHEDULE_BLOCKS.items():
        start_str, end_str = time_range.split("-")
        schedule.append({
            "start": start_str,
            "end": end_str,
            "type": block_type,
            "label": _block_label(block_type),
        })

    return schedule


def _block_label(block_type: str) -> str:
    labels = {
        "news": "نشرة إخبارية",
        "radio": "برنامج إذاعي",
        "quran": "القرآن الكريم",
        "podcast": "بودكاست",
        "authority": "بيان رسمي",
        "voiceover": "تعليق صوتي",
    }
    return labels.get(block_type, block_type)


def get_next_block_change() -> dict:
    """Return info about when the next schedule block change occurs."""

    now = datetime.now()
    now_mins = _minutes_since_midnight(now.hour, now.minute)
    current = get_current_block()

    closest_change = None
    closest_delta = float("inf")

    for time_range, block_type in config.SCHEDULE_BLOCKS.items():
        start_str, _ = time_range.split("-")
        sh, sm = _parse_time(start_str)
        start_mins = _minutes_since_midnight(sh, sm)

        delta = start_mins - now_mins
        if delta <= 0:
            delta += 1440  # wrap to next day

        if delta < closest_delta:
            closest_delta = delta
            closest_change = {
                "next_type": block_type,
                "next_label": _block_label(block_type),
                "minutes_until": delta,
                "at": start_str,
            }

    return {
        "current_type": current,
        "current_label": _block_label(current),
        **(closest_change or {}),
    }


if __name__ == "__main__":
    info = get_next_block_change()
    print(f"Current: {info['current_label']} ({info['current_type']})")
    print(f"Next: {info.get('next_label')} at {info.get('at')} ({info.get('minutes_until')}m)")

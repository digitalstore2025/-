"""
Quran-Conditioned Palestinian Broadcast AI — RSS Feed Integration

Fetches live news from Arabic RSS feeds, filters, and returns
broadcast-ready headline strings.
"""

import hashlib
import json
import time
from pathlib import Path

import feedparser

from config import CACHE_DIR, RSS_FEEDS, RSS_FETCH_INTERVAL
from logger import get_logger

log = get_logger("rss_feed")

_CACHE_FILE = CACHE_DIR / "rss_cache.json"
_SEEN_FILE = CACHE_DIR / "rss_seen.json"


def _load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def fetch_headlines(max_per_feed: int = 10) -> list[dict]:
    """Fetch latest headlines from configured RSS feeds.

    Returns a list of dicts: ``{"title": ..., "summary": ..., "link": ..., "source": ...}``
    """

    cache = _load_json(_CACHE_FILE)
    now = time.time()

    # Use cache if fresh
    if cache.get("ts") and (now - cache["ts"]) < RSS_FETCH_INTERVAL:
        log.debug("Using cached headlines (%d items)", len(cache.get("items", [])))
        return cache.get("items", [])

    items: list[dict] = []

    for feed_url in RSS_FEEDS:
        try:
            log.info("Fetching RSS: %s", feed_url)
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                items.append({
                    "title": title,
                    "summary": entry.get("summary", "").strip()[:300],
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                })

        except Exception as exc:
            log.warning("RSS fetch failed for %s: %s", feed_url, exc)

    # Save cache
    cache = {"ts": now, "items": items}
    _save_json(_CACHE_FILE, cache)

    log.info("Fetched %d headlines total", len(items))
    return items


def get_unseen_headlines(max_count: int = 5) -> list[str]:
    """Return up to *max_count* headline titles that haven't been broadcast yet."""

    seen = _load_json(_SEEN_FILE)
    headlines = fetch_headlines()

    unseen: list[str] = []
    for item in headlines:
        h = _hash(item["title"])
        if h not in seen:
            unseen.append(item["title"])
            seen[h] = time.time()
            if len(unseen) >= max_count:
                break

    _save_json(_SEEN_FILE, seen)
    return unseen


def get_full_bulletin(max_items: int = 5) -> str:
    """Build a single Arabic news bulletin string from unseen headlines."""

    headlines = get_unseen_headlines(max_items)

    if not headlines:
        return ""

    parts = ["بسم الله الرحمن الرحيم. إليكم أبرز عناوين الأخبار."]

    for i, h in enumerate(headlines, 1):
        parts.append(f"الخبر رقم {i}. {h}.")

    parts.append("كانت هذه أبرز العناوين. ابقوا معنا.")

    return " ".join(parts)

"""
Quran-Conditioned Palestinian Broadcast AI — RSS Feed Integration

Fetches live news from Arabic RSS feeds, filters, and returns
broadcast-ready headline strings.

Uses atoma for RSS parsing (feedparser has sgmllib issues on Python 3.11+).
Falls back gracefully if no RSS library is available.
"""

import hashlib
import json
import time
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

from config import CACHE_DIR, RSS_FEEDS, RSS_FETCH_INTERVAL
from logger import get_logger

log = get_logger("rss_feed")

_CACHE_FILE = CACHE_DIR / "rss_cache.json"
_SEEN_FILE = CACHE_DIR / "rss_seen.json"

# Try importing atoma, fall back to stdlib XML parsing
_USE_ATOMA = False
try:
    import atoma
    _USE_ATOMA = True
except ImportError:
    pass


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


def _fetch_xml(url: str, timeout: int = 15) -> bytes:
    """Fetch raw XML from a URL."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PalestinianBroadcastAI/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _parse_with_atoma(xml_bytes: bytes, max_items: int, feed_url: str) -> list[dict]:
    """Parse RSS/Atom feed using atoma."""
    items = []
    try:
        feed = atoma.parse_rss_bytes(xml_bytes)
        source = feed.title or feed_url
        for entry in feed.items[:max_items]:
            title = (entry.title or "").strip()
            if not title:
                continue
            items.append({
                "title": title,
                "summary": (entry.description or "").strip()[:300],
                "link": entry.link or "",
                "source": source,
            })
    except Exception:
        try:
            feed = atoma.parse_atom_bytes(xml_bytes)
            source = (feed.title and feed.title.value) or feed_url
            for entry in feed.entries[:max_items]:
                title = (entry.title and entry.title.value) or ""
                title = title.strip()
                if not title:
                    continue
                link = ""
                if entry.links:
                    link = entry.links[0].href or ""
                items.append({
                    "title": title,
                    "summary": "",
                    "link": link,
                    "source": source,
                })
        except Exception as exc:
            log.warning("atoma parse failed: %s", exc)
    return items


def _parse_with_stdlib(xml_bytes: bytes, max_items: int, feed_url: str) -> list[dict]:
    """Parse RSS feed using stdlib ElementTree (basic fallback)."""
    items = []
    try:
        root = ElementTree.fromstring(xml_bytes)

        # Try RSS 2.0
        channel = root.find("channel")
        if channel is not None:
            source = (channel.findtext("title") or feed_url).strip()
            for item in channel.findall("item")[:max_items]:
                title = (item.findtext("title") or "").strip()
                if not title:
                    continue
                items.append({
                    "title": title,
                    "summary": (item.findtext("description") or "").strip()[:300],
                    "link": item.findtext("link") or "",
                    "source": source,
                })
        else:
            # Try Atom
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            source = (root.findtext("atom:title", namespaces=ns) or feed_url).strip()
            for entry in root.findall("atom:entry", namespaces=ns)[:max_items]:
                title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                if not title:
                    continue
                link_el = entry.find("atom:link", namespaces=ns)
                link = link_el.get("href", "") if link_el is not None else ""
                items.append({
                    "title": title,
                    "summary": "",
                    "link": link,
                    "source": source,
                })
    except Exception as exc:
        log.warning("stdlib XML parse failed: %s", exc)
    return items


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
            xml_bytes = _fetch_xml(feed_url)

            if _USE_ATOMA:
                feed_items = _parse_with_atoma(xml_bytes, max_per_feed, feed_url)
            else:
                feed_items = _parse_with_stdlib(xml_bytes, max_per_feed, feed_url)

            items.extend(feed_items)
            log.info("  Got %d items from %s", len(feed_items), feed_url)

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

#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Quran Dataset Downloader

Downloads Quran recitation audio from EveryAyah.com (free, public API)
and builds the dataset_quran directory with proper metadata.csv.

Usage:
  python download_quran_dataset.py                    # Al-Fatiha (Surah 1)
  python download_quran_dataset.py --surah 1 2 3      # Specific surahs
  python download_quran_dataset.py --reciter husary    # Different reciter
  python download_quran_dataset.py --all-short         # All short surahs (78-114)

Reciters available:
  husary      — Sheikh Mahmoud Khalil Al-Husary (default, clear tajweed)
  minshawi    — Sheikh Muhammad Siddiq Al-Minshawi
  abdulbasit  — Sheikh Abdul Basit Abdul Samad
  sudais      — Sheikh Abdul Rahman Al-Sudais
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Ensure correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from logger import get_logger

log = get_logger("quran_download")

DATASET_DIR = Path("dataset_quran")
WAVS_DIR = DATASET_DIR / "wavs"
METADATA_FILE = DATASET_DIR / "metadata.csv"

# EveryAyah.com reciter base URLs (MP3)
RECITERS = {
    "husary": "https://everyayah.com/data/Husary_128kbps/",
    "minshawi": "https://everyayah.com/data/Minshawy_Murattal_128kbps/",
    "abdulbasit": "https://everyayah.com/data/Abdul_Basit_Murattal_192kbps/",
    "sudais": "https://everyayah.com/data/Abdurrahmaan_As-Sudais_192kbps/",
}

# Quran structure: surah_number -> (name_ar, ayah_count)
SURAH_INFO = {
    1: ("الفاتحة", 7),
    2: ("البقرة", 286), 36: ("يس", 83),
    55: ("الرحمن", 78), 56: ("الواقعة", 96),
    67: ("الملك", 30), 78: ("النبأ", 40),
    79: ("النازعات", 46), 80: ("عبس", 42),
    81: ("التكوير", 29), 82: ("الانفطار", 19),
    83: ("المطففين", 36), 84: ("الانشقاق", 25),
    85: ("البروج", 22), 86: ("الطارق", 17),
    87: ("الأعلى", 19), 88: ("الغاشية", 26),
    89: ("الفجر", 30), 90: ("البلد", 20),
    91: ("الشمس", 15), 92: ("الليل", 21),
    93: ("الضحى", 11), 94: ("الشرح", 8),
    95: ("التين", 8), 96: ("العلق", 19),
    97: ("القدر", 5), 98: ("البينة", 8),
    99: ("الزلزلة", 8), 100: ("العاديات", 11),
    101: ("القارعة", 11), 102: ("التكاثر", 8),
    103: ("العصر", 3), 104: ("الهمزة", 9),
    105: ("الفيل", 5), 106: ("قريش", 4),
    107: ("الماعون", 7), 108: ("الكوثر", 3),
    109: ("الكافرون", 6), 110: ("النصر", 3),
    111: ("المسد", 5), 112: ("الإخلاص", 4),
    113: ("الفلق", 5), 114: ("الناس", 6),
}

# Quran text (Al-Fatiha + Juz Amma selection for metadata)
# Full text mapping would be huge — we include commonly used verses
AYAH_TEXT = {
    "001001": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "001002": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "001003": "الرَّحْمَٰنِ الرَّحِيمِ",
    "001004": "مَالِكِ يَوْمِ الدِّينِ",
    "001005": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
    "001006": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
    "001007": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
    "112001": "قُلْ هُوَ اللَّهُ أَحَدٌ",
    "112002": "اللَّهُ الصَّمَدُ",
    "112003": "لَمْ يَلِدْ وَلَمْ يُولَدْ",
    "112004": "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
    "113001": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
    "113002": "مِن شَرِّ مَا خَلَقَ",
    "113003": "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ",
    "113004": "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ",
    "113005": "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ",
    "114001": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
    "114002": "مَلِكِ النَّاسِ",
    "114003": "إِلَٰهِ النَّاسِ",
    "114004": "مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ",
    "114005": "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ",
    "114006": "مِنَ الْجِنَّةِ وَالنَّاسِ",
    "103001": "وَالْعَصْرِ",
    "103002": "إِنَّ الْإِنسَانَ لَفِي خُسْرٍ",
    "103003": "إِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ",
    "108001": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ",
    "108002": "فَصَلِّ لِرَبِّكَ وَانْحَرْ",
    "108003": "إِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ",
    "110001": "إِذَا جَاءَ نَصْرُ اللَّهِ وَالْفَتْحُ",
    "110002": "وَرَأَيْتَ النَّاسَ يَدْخُلُونَ فِي دِينِ اللَّهِ أَفْوَاجًا",
    "110003": "فَسَبِّحْ بِحَمْدِ رَبِّكَ وَاسْتَغْفِرْهُ إِنَّهُ كَانَ تَوَّابًا",
}


def _download_file(url: str, dest: str, retries: int = 3) -> bool:
    """Download a file with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "PalestinianBroadcastAI/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                with open(dest, "wb") as f:
                    f.write(data)
            return True
        except Exception as exc:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                log.warning("Failed to download %s: %s", url, exc)
    return False


def _mp3_to_wav(mp3_path: str, wav_path: str) -> bool:
    """Convert MP3 to 22050 Hz mono WAV using ffmpeg."""
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", mp3_path,
                "-ar", "22050",
                "-ac", "1",
                wav_path,
            ],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_surah(
    surah_num: int,
    reciter: str = "husary",
) -> list[tuple[str, str]]:
    """Download all ayahs of a surah and return list of (wav_filename, text) tuples."""

    if surah_num not in SURAH_INFO:
        log.warning("Surah %d not in info table, skipping", surah_num)
        return []

    name_ar, ayah_count = SURAH_INFO[surah_num]
    base_url = RECITERS.get(reciter, RECITERS["husary"])

    log.info("Downloading Surah %d (%s) — %d ayahs [%s]", surah_num, name_ar, ayah_count, reciter)

    WAVS_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for ayah_num in range(1, ayah_count + 1):
        # EveryAyah format: SSSAAA.mp3 (e.g., 001001.mp3)
        filename = f"{surah_num:03d}{ayah_num:03d}"
        mp3_url = f"{base_url}{filename}.mp3"
        mp3_path = str(WAVS_DIR / f"{filename}.mp3")
        wav_path = str(WAVS_DIR / f"{filename}.wav")

        # Skip if WAV already exists
        if Path(wav_path).exists():
            text = AYAH_TEXT.get(filename, f"سورة {name_ar} الآية {ayah_num}")
            results.append((f"{filename}.wav", text))
            continue

        # Download MP3
        if not _download_file(mp3_url, mp3_path):
            continue

        # Convert to WAV
        if _mp3_to_wav(mp3_path, wav_path):
            text = AYAH_TEXT.get(filename, f"سورة {name_ar} الآية {ayah_num}")
            results.append((f"{filename}.wav", text))

            # Remove MP3 to save space
            Path(mp3_path).unlink(missing_ok=True)
        else:
            log.warning("ffmpeg conversion failed for %s", filename)

    log.info("  Downloaded %d/%d ayahs", len(results), ayah_count)
    return results


def build_metadata(entries: list[tuple[str, str]]):
    """Write/append metadata.csv for the Quran dataset."""

    existing = set()
    if METADATA_FILE.exists():
        with open(METADATA_FILE, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|", 1)
                if parts:
                    existing.add(parts[0])

    new_entries = [(f, t) for f, t in entries if f not in existing]

    if new_entries:
        with open(METADATA_FILE, "a", encoding="utf-8") as f:
            for wav_file, text in new_entries:
                f.write(f"{wav_file}|{text}\n")

    total = len(existing) + len(new_entries)
    log.info("metadata.csv: %d total entries (%d new)", total, len(new_entries))


def main():
    parser = argparse.ArgumentParser(
        description="Download Quran audio dataset for TTS training"
    )
    parser.add_argument(
        "--surah", type=int, nargs="+", default=[1],
        help="Surah numbers to download (default: 1 = Al-Fatiha)",
    )
    parser.add_argument(
        "--all-short", action="store_true",
        help="Download all short surahs (Juz Amma: 78-114)",
    )
    parser.add_argument(
        "--reciter", default="husary",
        choices=list(RECITERS.keys()),
        help="Reciter to use (default: husary)",
    )
    args = parser.parse_args()

    log.info("=" * 50)
    log.info("  Quran Dataset Downloader")
    log.info("=" * 50)

    if args.all_short:
        surahs = list(range(78, 115))
    else:
        surahs = args.surah

    all_entries = []

    for surah_num in surahs:
        entries = download_surah(surah_num, reciter=args.reciter)
        all_entries.extend(entries)

    if all_entries:
        build_metadata(all_entries)
        log.info("")
        log.info("Done! %d audio files downloaded to %s", len(all_entries), WAVS_DIR)
        log.info("metadata.csv updated at %s", METADATA_FILE)
    else:
        log.warning("No audio files were downloaded. Check network connection.")


if __name__ == "__main__":
    main()

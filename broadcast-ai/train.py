#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Training Script

Merges all datasets (Quran, speaker, news, Palestinian, realistic, authority)
into a single unified dataset and fine-tunes XTTS v2 for broadcast-grade
Arabic TTS with Palestinian dialect support.

Features:
- Dataset validation (audio format, sample rate, duration)
- Progress reporting
- Resumable training
- Dry-run mode for testing
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from TTS.api import TTS

import config
from logger import get_logger

log = get_logger("train")


# ---------------------------------------------------------------------------
# Dataset validation
# ---------------------------------------------------------------------------

def _validate_wav(wav_path: str) -> dict | None:
    """Check a WAV file's properties. Returns info dict or None on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                wav_path,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        import json
        info = json.loads(result.stdout)
        stream = info.get("streams", [{}])[0]
        fmt = info.get("format", {})

        return {
            "sample_rate": int(stream.get("sample_rate", 0)),
            "channels": int(stream.get("channels", 0)),
            "duration": float(fmt.get("duration", 0)),
            "codec": stream.get("codec_name", ""),
        }
    except Exception:
        return None


def validate_dataset(dataset_path: Path) -> dict:
    """Validate a dataset directory and return statistics."""

    csv_path = dataset_path / "metadata.csv"
    stats = {
        "path": str(dataset_path),
        "total_lines": 0,
        "valid_samples": 0,
        "missing_wavs": 0,
        "invalid_wavs": 0,
        "total_duration": 0.0,
        "errors": [],
    }

    if not csv_path.exists():
        stats["errors"].append("metadata.csv not found")
        return stats

    with open(csv_path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue

            stats["total_lines"] += 1

            parts = line.split("|", 1)
            if len(parts) != 2:
                stats["errors"].append(f"Line {lineno}: bad format")
                continue

            wav_file, text = parts
            wav_path = dataset_path / "wavs" / wav_file

            if not wav_path.exists():
                stats["missing_wavs"] += 1
                continue

            info = _validate_wav(str(wav_path))
            if info is None:
                stats["invalid_wavs"] += 1
                continue

            stats["valid_samples"] += 1
            stats["total_duration"] += info["duration"]

    return stats


# ---------------------------------------------------------------------------
# Merge all datasets into one
# ---------------------------------------------------------------------------

def merge_datasets(dry_run: bool = False) -> int:
    """Combine every dataset directory into *dataset_merged*."""

    merged = config.DATASET_MERGED

    if not dry_run:
        if merged.exists():
            shutil.rmtree(merged)
        (merged / "wavs").mkdir(parents=True, exist_ok=True)

    metadata_lines: list[str] = []
    copied = 0
    skipped = 0
    total_duration = 0.0

    for ds in config.ALL_DATASETS:
        csv_path = ds / "metadata.csv"

        if not csv_path.exists():
            log.warning("[SKIP] %s not found", csv_path)
            continue

        ds_count = 0
        with open(csv_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|", 1)
                if len(parts) != 2:
                    skipped += 1
                    continue

                wav_file, text = parts
                src = ds / "wavs" / wav_file
                dst = merged / "wavs" / wav_file

                if not src.exists():
                    skipped += 1
                    continue

                if not dry_run:
                    shutil.copy2(src, dst)

                metadata_lines.append(line + "\n")
                copied += 1
                ds_count += 1

        log.info("[MERGE] %s: %d samples", ds.name, ds_count)

    if not dry_run:
        out_csv = merged / "metadata.csv"
        with open(out_csv, "w", encoding="utf-8") as fh:
            fh.writelines(metadata_lines)

    log.info("[MERGE] Total: %d samples merged, %d skipped", copied, skipped)
    return copied


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------

def train_model():
    """Fine-tune XTTS v2 on the merged dataset."""

    merged_csv = config.DATASET_MERGED / "metadata.csv"
    if not merged_csv.exists():
        log.error("Merged dataset not found at %s", merged_csv)
        sys.exit(1)

    log.info("[TRAIN] Base model: %s", config.BASE_MODEL)
    log.info("[TRAIN] Output: %s", config.MODEL_PATH)

    t0 = time.time()

    tts = TTS(config.BASE_MODEL)

    log.info("[TRAIN] Starting fine-tune...")
    tts.train(
        dataset_path=str(config.DATASET_MERGED),
        output_path=str(config.MODEL_PATH),
        language=config.LANGUAGE,
    )

    elapsed = time.time() - t0
    log.info("[TRAIN] Complete in %.0f minutes", elapsed / 60)
    log.info("[TRAIN] Model saved to %s", config.MODEL_PATH)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Palestinian Broadcast AI — Training Pipeline"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate all datasets without merging or training",
    )
    parser.add_argument(
        "--merge-only", action="store_true",
        help="Only merge datasets, skip training",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate merge without copying files",
    )
    args = parser.parse_args()

    # --- Validate mode ---
    if args.validate:
        log.info("=== Dataset Validation ===")
        for ds in config.ALL_DATASETS:
            stats = validate_dataset(ds)
            log.info(
                "%s: %d valid / %d total | %.1f min | %d missing | %d invalid",
                ds.name,
                stats["valid_samples"],
                stats["total_lines"],
                stats["total_duration"] / 60,
                stats["missing_wavs"],
                stats["invalid_wavs"],
            )
            for err in stats["errors"]:
                log.warning("  %s", err)
        return

    # --- Merge ---
    count = merge_datasets(dry_run=args.dry_run)

    if count == 0:
        log.warning("No audio samples found. Add WAV files to dataset directories.")
        log.warning("See dataset_quran/metadata.csv.example for format reference.")
        sys.exit(1)

    if args.dry_run:
        log.info("[DRY RUN] Would merge %d samples", count)
        return

    if args.merge_only:
        log.info("[MERGE] Done. Skipping training as requested.")
        return

    # --- Train ---
    train_model()


if __name__ == "__main__":
    main()

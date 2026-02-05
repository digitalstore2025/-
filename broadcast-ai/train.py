#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Training Script

Merges all datasets (Quran, speaker, news, Palestinian, realistic, authority)
into a single unified dataset and fine-tunes XTTS v2 for broadcast-grade
Arabic TTS with Palestinian dialect support.
"""

import os
import shutil
import sys

from TTS.api import TTS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

DATASETS = [
    "dataset_speaker",
    "dataset_speaker_news",
    "dataset_speaker_palestinian",
    "dataset_speaker_realistic",
    "dataset_authority",
]

QURAN_DATASET = "dataset_quran"

MERGED_DATASET = "dataset_merged"

OUTPUT_DIR = "models/final_broadcast_model"

# ---------------------------------------------------------------------------
# Merge all datasets into one
# ---------------------------------------------------------------------------

def merge_datasets():
    """Combine every dataset directory into *dataset_merged*."""

    if os.path.exists(MERGED_DATASET):
        shutil.rmtree(MERGED_DATASET)

    os.makedirs(os.path.join(MERGED_DATASET, "wavs"), exist_ok=True)

    metadata_lines: list[str] = []
    copied = 0

    all_datasets = DATASETS + [QURAN_DATASET]

    for ds in all_datasets:
        csv_path = os.path.join(ds, "metadata.csv")

        if not os.path.exists(csv_path):
            print(f"[SKIP] {csv_path} not found")
            continue

        with open(csv_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|", 1)
                if len(parts) != 2:
                    continue

                wav_file, text = parts
                src = os.path.join(ds, "wavs", wav_file)
                dst = os.path.join(MERGED_DATASET, "wavs", wav_file)

                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    metadata_lines.append(line + "\n")
                    copied += 1

    out_csv = os.path.join(MERGED_DATASET, "metadata.csv")
    with open(out_csv, "w", encoding="utf-8") as fh:
        fh.writelines(metadata_lines)

    print(f"[MERGE] {copied} samples written to {MERGED_DATASET}/")
    return copied


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------

def train_model():
    """Fine-tune XTTS v2 on the merged dataset."""

    if not os.path.exists(os.path.join(MERGED_DATASET, "metadata.csv")):
        print("[ERROR] Merged dataset not found. Run merge first.")
        sys.exit(1)

    print(f"[TRAIN] Loading base model: {BASE_MODEL}")
    tts = TTS(BASE_MODEL)

    print(f"[TRAIN] Starting fine-tune → {OUTPUT_DIR}")
    tts.train(
        dataset_path=MERGED_DATASET,
        output_path=OUTPUT_DIR,
        language="ar",
    )

    print(f"[TRAIN] Model saved to {OUTPUT_DIR}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    count = merge_datasets()

    if count == 0:
        print("[WARN] No audio samples found. Add WAV files to dataset directories.")
        print("       See dataset_quran/metadata.csv.example for format reference.")
        sys.exit(1)

    train_model()

"""
Quran-Conditioned Palestinian Broadcast AI — Logging

Structured, levelled logging with both console and file output.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_FMT = "[%(asctime)s] %(levelname)-8s %(name)-20s  %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with console + rotating file handlers."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
    logger.addHandler(ch)

    # File (daily rotation by name)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{name}_{today}.log"
    fh = logging.FileHandler(str(log_file), encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
    logger.addHandler(fh)

    return logger

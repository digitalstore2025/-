"""
Quran-Conditioned Palestinian Broadcast AI — Configuration

Centralized configuration with environment variable overrides.
All paths, model settings, audio parameters, and server config live here.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Datasets
DATASET_QURAN = BASE_DIR / "dataset_quran"
DATASET_SPEAKER = BASE_DIR / "dataset_speaker"
DATASET_SPEAKER_NEWS = BASE_DIR / "dataset_speaker_news"
DATASET_SPEAKER_PALESTINIAN = BASE_DIR / "dataset_speaker_palestinian"
DATASET_SPEAKER_REALISTIC = BASE_DIR / "dataset_speaker_realistic"
DATASET_AUTHORITY = BASE_DIR / "dataset_authority"
DATASET_MERGED = BASE_DIR / "dataset_merged"

ALL_DATASETS = [
    DATASET_SPEAKER,
    DATASET_SPEAKER_NEWS,
    DATASET_SPEAKER_PALESTINIAN,
    DATASET_SPEAKER_REALISTIC,
    DATASET_AUTHORITY,
    DATASET_QURAN,
]

# Model
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "final_broadcast_model"
BASE_MODEL = os.environ.get(
    "BASE_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2"
)

# Wav2Lip
WAV2LIP_DIR = BASE_DIR / "Wav2Lip"
WAV2LIP_INFERENCE = WAV2LIP_DIR / "inference.py"
WAV2LIP_CHECKPOINT = MODEL_DIR / "wav2lip.pth"

# I/O
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
ANCHOR_IMAGE = INPUT_DIR / "anchor.jpg"
ANCHOR_VIDEO = INPUT_DIR / "anchor.mp4"
REFERENCE_WAV = DATASET_SPEAKER / "wavs" / "0001.wav"

# Logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Cache
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

SAMPLE_RATE = 22050
AUDIO_CHANNELS = 1  # mono
AUDIO_FORMAT = "wav"
LANGUAGE = "ar"

# ffmpeg broadcast EQ chain
FFMPEG_AF_CHAIN = (
    "highpass=f=80,"
    "lowpass=f=8000,"
    "loudnorm=I=-16:LRA=11:TP=-1.5"
)

# Style-specific EQ overrides
STYLE_EQ = {
    "news": "highpass=f=80,lowpass=f=8000,loudnorm=I=-16:LRA=11:TP=-1.5",
    "radio": "highpass=f=60,lowpass=f=10000,loudnorm=I=-14:LRA=13:TP=-1.0",
    "podcast": "highpass=f=70,lowpass=f=12000,loudnorm=I=-18:LRA=9:TP=-2.0",
    "voiceover": "highpass=f=100,lowpass=f=7000,loudnorm=I=-20:LRA=7:TP=-2.0",
    "authority": "highpass=f=80,lowpass=f=8000,loudnorm=I=-14:LRA=11:TP=-1.0",
    "quran": "highpass=f=50,lowpass=f=14000,loudnorm=I=-20:LRA=7:TP=-2.0",
}

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

SERVER_HOST = os.environ.get("HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("PORT", 3000))
RADIO_PORT = int(os.environ.get("RADIO_PORT", 3001))

# ---------------------------------------------------------------------------
# RSS Feeds
# ---------------------------------------------------------------------------

RSS_FEEDS = [
    "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4571-a233-01a5a2f4a960/73d0e1b4-532f-45ef-b135-bba0b159cb86",
    "https://www.alaraby.co.uk/rss",
]

RSS_FETCH_INTERVAL = int(os.environ.get("RSS_INTERVAL", 300))  # seconds

# ---------------------------------------------------------------------------
# Broadcast Scheduling
# ---------------------------------------------------------------------------

BROADCAST_LOOP_PAUSE = int(os.environ.get("LOOP_PAUSE", 5))

SCHEDULE_BLOCKS = {
    "00:00-06:00": "quran",
    "06:00-06:30": "news",
    "06:30-09:00": "radio",
    "09:00-09:30": "news",
    "09:30-12:00": "radio",
    "12:00-12:30": "news",
    "12:30-15:00": "podcast",
    "15:00-15:30": "news",
    "15:30-18:00": "radio",
    "18:00-18:30": "news",
    "18:30-21:00": "podcast",
    "21:00-21:30": "news",
    "21:30-00:00": "quran",
}

# ---------------------------------------------------------------------------
# Content pool
# ---------------------------------------------------------------------------

NEWS_HEADLINES = [
    "هنا غزة من إذاعة صوت القدس",
    "نوافيكم بآخر الأخبار من فلسطين",
    "تواصل الجهات المختصة متابعة الأوضاع الميدانية",
    "نبقى معكم في متابعة مستمرة على مدار الساعة",
    "بسم الله الرحمن الرحيم نقدم لكم النشرة الإخبارية",
    "آخر المستجدات من الميدان الفلسطيني",
    "صوت فلسطين يوافيكم بالتطورات الأخيرة",
    "أهلاً بكم في نشرة أخبار صوت القدس",
]

RADIO_INTROS = [
    "أهلاً وسهلاً بكم في إذاعة صوت القدس",
    "معكم من استوديوهات صوت فلسطين",
    "طابت أوقاتكم مع إذاعتكم صوت القدس",
    "نحييكم من أرض فلسطين الحبيبة",
    "صباح الخير من إذاعة صوت القدس",
    "مساء النور على أهلنا في كل مكان",
]

QURAN_SEGMENTS = [
    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "الرَّحْمَٰنِ الرَّحِيمِ",
    "مَالِكِ يَوْمِ الدِّينِ",
    "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
    "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
]

AUTHORITY_STATEMENTS = [
    "بيان رسمي صادر عن المكتب الإعلامي",
    "تصريح عاجل من المتحدث الرسمي",
    "نؤكد على ضرورة الالتزام بالتعليمات",
    "ندعو جميع المواطنين إلى التزام الحذر",
    "المصادر الرسمية تؤكد صحة هذه المعلومات",
]

PODCAST_INTROS = [
    "أهلاً بكم في بودكاست صوت القدس",
    "مرحباً بكم في حلقة جديدة من بودكاست فلسطين",
    "معكم في حلقة جديدة نناقش فيها أهم المستجدات",
]

# Quran-Conditioned Palestinian AI Broadcast System

Complete end-to-end pipeline for broadcast-grade Arabic text-to-speech (TTS) with Palestinian dialect support, conditioned on Quranic recitation patterns for authentic pronunciation.

## 🎯 Overview

This system provides:

- **Fine-tuned XTTS v2 model** trained on multiple Arabic datasets (Quran, news, Palestinian dialect, realistic speech, authority statements)
- **Broadcast-grade audio processing** with EBU R128 loudness normalization
- **Lip-synced video generation** using Wav2Lip
- **Live streaming server** with web-based player
- **Continuous TV channel loop** for automated broadcast

## 📋 System Requirements

- Python 3.8+
- FFmpeg
- 8GB+ RAM (16GB recommended for training)
- CUDA-capable GPU (optional but highly recommended for training)

## 🚀 Quick Start

### 1. Setup

Run the automated setup script:

```bash
cd broadcast-ai
./setup.sh
```

This will:
- Install system dependencies (ffmpeg)
- Install Python packages from `requirements.txt`
- Create all necessary directory structures

### 2. Prepare Datasets

Add your audio files and metadata to the dataset directories:

```
dataset_quran/
  wavs/
    001001.wav
    001002.wav
    ...
  metadata.csv

dataset_speaker/
  wavs/
    0001.wav
    0002.wav
    ...
  metadata.csv

dataset_speaker_news/
  wavs/
    news_001.wav
    ...
  metadata.csv

dataset_speaker_palestinian/
  wavs/
    pal_001.wav
    ...
  metadata.csv

dataset_speaker_realistic/
  wavs/
    real_001.wav
    ...
  metadata.csv

dataset_authority/
  wavs/
    auth_001.wav
    ...
  metadata.csv
```

**Metadata Format** (`metadata.csv`):

```
filename.wav|Arabic text transcription
```

See `*.csv.example` files in each dataset directory for examples.

### 3. Train the Model

Merge all datasets and fine-tune XTTS v2:

```bash
python train.py
```

This will:
1. Merge all datasets into `dataset_merged/`
2. Fine-tune XTTS v2 on the combined dataset
3. Save the model to `models/final_broadcast_model/`

**Note**: Training can take several hours depending on your hardware and dataset size.

### 4. Generate Voice

Test voice generation:

```bash
python generate.py
```

This generates a demo audio file at `output/demo.wav` with broadcast-grade processing:
- High-pass filter at 80 Hz (removes rumble)
- Low-pass filter at 8000 Hz (removes hiss)
- EBU R128 loudness normalization (-16 LUFS)

### 5. Run TV Channel (Optional)

For continuous broadcast with lip-synced video:

**Prerequisites**:
- Clone and setup [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
- Download the Wav2Lip checkpoint to `models/wav2lip.pth`
- Place an anchor image at `input/anchor.jpg`

**Run**:

```bash
# Terminal 1 - Generate segments
python run_tv_channel.py

# Terminal 2 - Start web server
python tv_server.py
```

Access the live stream at `http://localhost:3000`

## 📁 Project Structure

```
broadcast-ai/
├── train.py                    # Training script
├── generate.py                 # Voice generation
├── run_tv_channel.py          # TV channel loop
├── tv_server.py               # Flask streaming server
├── setup.sh                   # Setup script
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
│
├── dataset_quran/             # Quranic recitations
├── dataset_speaker/           # Base speaker samples
├── dataset_speaker_news/      # News-style speech
├── dataset_speaker_palestinian/  # Palestinian dialect
├── dataset_speaker_realistic/ # Realistic conversational
├── dataset_authority/         # Authority statements
│
├── models/                    # Trained models
│   └── final_broadcast_model/ # Fine-tuned XTTS v2
│
├── input/                     # Input media (anchor image/video)
├── output/                    # Generated audio/video
└── dataset_merged/            # Merged dataset (auto-generated)
```

## 🎙️ Voice Generation API

```python
from generate import generate_voice

# Generate speech
audio_path = generate_voice(
    text="هنا غزة، من إذاعة صوت القدس. نوافيكم بآخر الأخبار.",
    style="news",
    output_name="my_audio.wav"
)
```

**Parameters**:
- `text`: Arabic text to synthesize
- `style`: Style hint (reserved for future use)
- `output_name`: Output filename in `output/` directory

## 🌐 Web Server Routes

- `/` - HTML player page (RTL Arabic interface)
- `/stream` - Direct video/audio stream
- `/health` - JSON health check endpoint

## 📊 Dataset Guidelines

For best results:

1. **Audio Quality**: 
   - 16kHz+ sample rate
   - Clean, noise-free recordings
   - Consistent volume levels

2. **Dataset Balance**:
   - Aim for 100+ samples per dataset
   - Mix formal and informal speech
   - Include various speaking styles

3. **Transcription**:
   - Use proper Arabic Unicode
   - Include diacritics for Quran dataset
   - Keep transcriptions accurate

## 🔧 Customization

### Changing Reference Voice

Edit `generate.py`:

```python
REFERENCE_WAV = "dataset_speaker/wavs/your_reference.wav"
```

### Adjusting Audio Processing

Modify the FFmpeg filter chain in `generate.py`:

```python
af_chain = (
    "highpass=f=80,"
    "lowpass=f=8000,"
    "loudnorm=I=-16:LRA=11:TP=-1.5"
)
```

### Adding News Headlines

Edit the `NEWS_HEADLINES` list in `run_tv_channel.py`:

```python
NEWS_HEADLINES = [
    "Your custom headline 1",
    "Your custom headline 2",
    # ...
]
```

## 🐛 Troubleshooting

### Model Not Found Error

Ensure you've run `python train.py` first to create the model.

### FFmpeg Not Found

Install FFmpeg:
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from [ffmpeg.org](https://ffmpeg.org)

### Out of Memory During Training

Reduce batch size or use a machine with more RAM/GPU memory.

### Wav2Lip Not Working

Make sure:
1. Wav2Lip is cloned in the same parent directory
2. Checkpoint file exists at `models/wav2lip.pth`
3. Anchor video exists at `input/anchor.mp4`

## 📝 License

This is an open-source project created for humanitarian and educational purposes.

## 🙏 Acknowledgments

- [Coqui TTS](https://github.com/coqui-ai/TTS) for XTTS v2
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) for lip-sync technology
- The Palestinian people for their resilience and inspiration

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**صوت القدس — Voice of Jerusalem** 🇵🇸

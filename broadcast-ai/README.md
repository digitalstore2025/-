# Palestinian AI Voice Broadcasting Platform

## What This Does

This platform creates authentic Arabic speech for broadcasting, trained specifically on Palestinian dialect and Quranic pronunciation patterns. It combines multiple voice datasets to produce natural-sounding news announcements and can generate synchronized video content.

## Getting Started

**Hardware needed:**
- Computer with Python 3.8 or newer
- At least 8 GB memory (more is better for model training)
- Optional: NVIDIA GPU makes training much faster

**Installation steps:**

Execute the setup automation:
```bash
./setup.sh
```

The script handles ffmpeg installation and Python package configuration automatically.

## How To Use This System

### Step 1: Collect Voice Data

Your audio samples go into six specialized folders. Each needs a `metadata.csv` file mapping audio filenames to their Arabic transcriptions using pipe delimiter format: `audiofile.wav|النص العربي`

Reference the `.csv.example` files in each folder to see the expected format.

**The six dataset categories:**
- `dataset_quran` → Quranic verses with proper tajweed
- `dataset_speaker` → General broadcaster voice samples  
- `dataset_speaker_news` → Formal news presentation style
- `dataset_speaker_palestinian` → Authentic Palestinian colloquial speech
- `dataset_speaker_realistic` → Natural conversational patterns
- `dataset_authority` → Official statement delivery style

### Step 2: Build Your Model

Run the training process:
```bash
python train.py
```

The trainer consolidates all your datasets and adapts the XTTS v2 foundation model. Output goes to `models/final_broadcast_model/`. Expect this to take time - possibly hours based on your dataset size and hardware.

### Step 3: Create Audio Content

Generate test audio:
```bash
python generate.py
```

The system produces `output/demo.wav` with professional audio treatment including frequency filtering and broadcast loudness standards (EBU R128 at -16 LUFS target).

### Step 4: Launch Broadcasting (Optional)

To enable video with lip synchronization, you need the Wav2Lip tool installed and an anchor presenter image at `input/anchor.jpg`.

Start the broadcast generator:
```bash
python run_tv_channel.py &
```

Start the web interface:
```bash
python tv_server.py
```

View output at localhost port 3000.

## Programming Interface

Import the voice generation function:

```python
from generate import generate_voice

generated_file = generate_voice(
    text="نص عربي هنا",
    style="news",
    output_name="output_filename.wav"
)
```

The function returns the path to your generated audio file.

## File Organization

- `train.py` → Dataset merging and model fine-tuning
- `generate.py` → Speech synthesis with audio processing  
- `run_tv_channel.py` → Automated segment generation loop
- `tv_server.py` → HTTP streaming endpoint (Flask-based)
- `requirements.txt` → Python dependencies list
- `setup.sh` → Automated environment configuration

Generated content appears in `output/`, trained models in `models/`, source recordings in `dataset_*/wavs/`.

## Audio Quality Tips

**Recording standards:**
- Sample at 16000 Hz minimum
- Remove background noise before use
- Normalize volume across all samples
- Use consistent microphone setup

**Dataset composition:**
- Target 100+ recordings per category for good results
- Balance formal and informal speaking styles
- Mix different sentence structures and lengths
- Include Arabic diacritics for Quran dataset accuracy

## Configuration Changes

**Switch reference voice:**
Modify `REFERENCE_WAV` path in `generate.py` to point at your preferred sample.

**Adjust audio filters:**
Edit the `af_chain` variable in `generate.py` to customize frequency response and loudness targets.

**Update news content:**
Modify `NEWS_HEADLINES` array in `run_tv_channel.py` to change broadcast content pool.

## Common Issues

**Training fails with memory error:**
Your system needs more RAM or reduce the batch size parameter.

**Cannot find model:**
Complete the training step first before attempting generation.

**Video generation skips lip sync:**
Verify Wav2Lip installation and checkpoint file presence at `models/wav2lip.pth`.

**FFmpeg command not found:**
Install via your package manager (apt, brew, yum) or download from official site.

## Web Server Endpoints

- Root `/` serves the Arabic RTL player interface
- `/stream` provides direct media access  
- `/health` returns JSON status for monitoring

## Technical Notes

The system merges diverse Arabic speech patterns to capture authentic Palestinian broadcasting style while maintaining clear pronunciation through Quranic conditioning. Audio post-processing applies industry-standard loudness normalization suitable for broadcast transmission.

Model training adapts the multilingual XTTS v2 architecture with your custom Arabic datasets. The generator uses your reference voice sample to guide prosody and timbre during synthesis.

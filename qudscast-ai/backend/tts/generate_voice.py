#!/usr/bin/env python3
"""
QudsCast AI - Voice Generation Script
Arabic TTS with Voice Cloning using Coqui XTTS v2
"""

import argparse
import os
import sys

def generate_with_xtts(text, voice_sample, output_path, language='ar'):
    """Generate voice using Coqui XTTS v2"""
    try:
        from TTS.api import TTS

        # Initialize XTTS model
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

        # Generate with voice cloning
        tts.tts_to_file(
            text=text,
            speaker_wav=voice_sample,
            language=language,
            file_path=output_path,
            speed=0.95
        )

        print(f"Voice generated successfully: {output_path}")
        return True

    except ImportError:
        print("TTS library not installed, trying alternative...")
        return False
    except Exception as e:
        print(f"XTTS error: {e}")
        return False

def generate_with_gtts(text, output_path, language='ar'):
    """Fallback: Generate voice using gTTS (Google TTS)"""
    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang=language, slow=False)

        # gTTS outputs MP3
        mp3_path = output_path.replace('.wav', '.mp3')
        tts.save(mp3_path)

        # Convert to WAV using ffmpeg if needed
        if output_path.endswith('.wav'):
            import subprocess
            subprocess.run([
                'ffmpeg', '-y', '-i', mp3_path,
                '-acodec', 'pcm_s16le', '-ar', '22050',
                output_path
            ], check=True)
            os.remove(mp3_path)
        else:
            os.rename(mp3_path, output_path)

        print(f"Voice generated with gTTS: {output_path}")
        return True

    except ImportError:
        print("gTTS not installed")
        return False
    except Exception as e:
        print(f"gTTS error: {e}")
        return False

def generate_with_espeak(text, output_path, language='ar'):
    """Fallback: Generate voice using espeak-ng"""
    try:
        import subprocess

        result = subprocess.run([
            'espeak-ng',
            '-v', language,
            '-s', '130',  # Speed
            '-w', output_path,
            text
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Voice generated with espeak-ng: {output_path}")
            return True
        else:
            print(f"espeak-ng error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("espeak-ng not installed")
        return False
    except Exception as e:
        print(f"espeak-ng error: {e}")
        return False

def generate_with_piper(text, output_path, model='ar_JO-kareem-medium'):
    """Fallback: Generate voice using Piper TTS"""
    try:
        import subprocess

        process = subprocess.Popen(
            ['piper', '--model', model, '--output_file', output_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate(input=text.encode('utf-8'))

        if process.returncode == 0:
            print(f"Voice generated with Piper: {output_path}")
            return True
        else:
            print(f"Piper error: {stderr.decode()}")
            return False

    except FileNotFoundError:
        print("Piper not installed")
        return False
    except Exception as e:
        print(f"Piper error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate Arabic voice for news broadcast')
    parser.add_argument('--model', type=str, default='xtts_v2', help='TTS model to use')
    parser.add_argument('--voice', type=str, help='Path to voice sample WAV file')
    parser.add_argument('--text', type=str, help='Path to text file or direct text')
    parser.add_argument('--out', type=str, required=True, help='Output audio file path')
    parser.add_argument('--lang', type=str, default='ar', help='Language code')

    args = parser.parse_args()

    # Get text content
    if args.text and os.path.isfile(args.text):
        with open(args.text, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Error: No text provided")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    # Try generation methods in order of preference
    success = False

    # 1. Try XTTS v2 with voice cloning
    if args.voice and os.path.exists(args.voice):
        success = generate_with_xtts(text, args.voice, args.out, args.lang)

    # 2. Try Piper (fast and good quality)
    if not success:
        success = generate_with_piper(text, args.out)

    # 3. Try gTTS (requires internet)
    if not success:
        success = generate_with_gtts(text, args.out, args.lang)

    # 4. Try espeak-ng (lowest quality but always available)
    if not success:
        success = generate_with_espeak(text, args.out, args.lang)

    if not success:
        print("Error: All TTS methods failed")
        sys.exit(1)

    print("Voice generation completed successfully")
    sys.exit(0)

if __name__ == '__main__':
    main()

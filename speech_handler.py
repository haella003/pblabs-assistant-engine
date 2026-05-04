import os
import re
import wave
import pygame
import sys
from pathlib import Path

# --- PORTABLE PATH LOGIC ---
BASE_DIR = Path(__file__).resolve().parent

# Automatically find the site-packages inside your venv
# This works for any user and any OS
VENV_PACKAGES = next(BASE_DIR.glob("venv/lib/python*/site-packages"), None)

if VENV_PACKAGES and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

# Now we import the actual engine from the venv
from piper.voice import PiperVoice

# Paths for data
PIPER_VOICES_DIR = BASE_DIR / "venv" / "piper_voices"
OUTPUT_FILE = str(BASE_DIR / "output_edi.wav")
MODEL_PATH = str(PIPER_VOICES_DIR / "en_US-amy-medium.onnx")

def speak(text):
    try:
        # Clean the text (remove emotion tags)
        clean_text = re.sub(r"\[.*?\]\s*\|\s*", "", text)
        clean_text = clean_text.replace('"', '').replace("'", "")
        if not clean_text.strip(): return

        print(f"--- EDI SPEAKING: {clean_text[:50]}... ---")

        # Load Piper and synthesize
        voice = PiperVoice.load(MODEL_PATH)
        with wave.open(OUTPUT_FILE, "wb") as wav_file:
            voice.synthesize(clean_text, wav_file)

        # Playback
        if os.path.exists(OUTPUT_FILE):
            pygame.mixer.init()
            pygame.mixer.music.load(OUTPUT_FILE)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()

    except Exception as e:
        print(f"Voice Error: {e}")
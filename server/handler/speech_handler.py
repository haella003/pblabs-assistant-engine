import os
import re
import wave
import sys
from pathlib import Path
import gc
import io
import uuid

# --- PORTABLE PATH LOGIC ---
HANDLER_DIR = Path(__file__).resolve().parent
BASE_DIR = HANDLER_DIR.parent.parent

VENV_PACKAGES = next(BASE_DIR.glob("venv/lib/python*/site-packages"), None)
if VENV_PACKAGES and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

from piper.voice import PiperVoice

PIPER_VOICES_DIR = "piper_voices"
MODEL_PATH = str(BASE_DIR / "server/piper_voices/en_US-amy-medium.onnx")

piper_voice = None

def load_model():
    """Loads the TTS model into memory."""
    global piper_voice
    if piper_voice is None:
        print("--- LOADING PIPER TTS MODEL ---")
        piper_voice = PiperVoice.load(MODEL_PATH)

def unload_model():
    """Unloads the TTS model from memory."""
    global piper_voice
    piper_voice = None
    gc.collect()

def generate_speech(text):
    """Generates speech using a temporary file to ensure Piper compatibility."""
    try:
        if piper_voice is None:
            load_model()

        clean_text = re.sub(r"\[.*?\]\s*\|\s*", "", text)
        clean_text = clean_text.replace('"', '').replace("'", "")
        
        # Create a unique temp filename
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        
        # 1. Open a real file for Piper to write to
        with open(temp_filename, "wb") as f:
            piper_voice.synthesize(clean_text, f)
        
        # 2. Read the bytes back from the file
        with open(temp_filename, "rb") as f:
            raw_audio_bytes = f.read()
            
        # 3. Delete the temporary file immediately
        os.remove(temp_filename)
        
        if not raw_audio_bytes or len(raw_audio_bytes) < 100:
            print("Voice Error: Piper output was too small.")
            return None
            
        return raw_audio_bytes

    except Exception as e:
        print(f"Voice Error: {e}")
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            os.remove(temp_filename)
        return None
import re
import wave
import sys
from pathlib import Path
import gc
import io

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
    """Generates speech and returns the raw WAV bytes entirely in memory."""
    try:
        if piper_voice is None:
            load_model()

        clean_text = re.sub(r"\[.*?\]\s*\|\s*", "", text)
        clean_text = clean_text.replace('"', '').replace("'", "")
        if not clean_text.strip(): 
            return None

        print(f"--- GENERATING SPEECH: {clean_text[:50]}... ---")

        # Use an in-memory buffer instead of saving to disk
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, "wb") as wav_file:
            piper_voice.synthesize(clean_text, wav_file)

        # Return the raw bytes from the buffer
        return audio_buffer.getvalue()

    except Exception as e:
        print(f"Voice Error: {e}")
        return None
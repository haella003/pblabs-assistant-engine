import os
import re
import uuid
import time
import subprocess
import sys
import gc
from pathlib import Path

# --- PORTABLE PATH LOGIC ---
HANDLER_DIR = Path(__file__).resolve().parent
BASE_DIR = HANDLER_DIR.parent.parent

# Ensure venv packages are in path
VENV_PACKAGES = next(BASE_DIR.glob("venv/lib/python*/site-packages"), None)
if VENV_PACKAGES and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

from piper.voice import PiperVoice

PIPER_EXE = os.path.join(BASE_DIR, "venv/bin/piper")
MODEL_PATH = os.path.join(BASE_DIR, "server/piper_voices/en_US-amy-medium.onnx")

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

# --- EDI BRAIN ---
def generate_speech(text):
    """M4-Verified: Uses the Piper binary directly."""
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    
    # Clean text (remove emotion tags and quotes)
    clean_text = re.sub(r"\[.*?\]\s*\|\s*", "", text)
    clean_text = clean_text.replace('"', '').replace("'", "")

    try:
        # The command that worked in your test_voice.py
        command = [
            PIPER_EXE,
            "--model", MODEL_PATH,
            "--output_file", temp_filename
        ]
        
        # Open process and send text via stdin
        process = subprocess.Popen(
            command, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        process.communicate(input=clean_text)

        # Verify the file was created and has data
        if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 44:
            with open(temp_filename, "rb") as f:
                raw_audio_bytes = f.read()
            
            # Clean up the temp file
            os.remove(temp_filename)
            print(f"M4 Binary Success: {len(raw_audio_bytes)} bytes.")
            return raw_audio_bytes
        else:
            print("M4 Binary Error: Output file was empty or missing.")
            if os.path.exists(temp_filename): os.remove(temp_filename)
            return None

    except Exception as e:
        print(f"Subprocess Error: {e}")
        return None
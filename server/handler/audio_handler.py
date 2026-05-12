import numpy as np
from faster_whisper import WhisperModel
import gc
import io

# EARS

whisper_model = None

def load_model():
    """Loads the model into memory when a session starts."""
    global whisper_model
    if whisper_model is None:
        print("--- LOADING LOCAL WHISPER MODEL ---")
        # Ensure compute_type matches your hardware capabilities
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def unload_model():
    """Unloads the model from memory to free up resources."""
    global whisper_model
    whisper_model = None
    gc.collect()

def transcribe_audio(audio_data: io.BytesIO):
    """Takes an in-memory audio byte stream, transcribes it, and returns the text."""
    print("--- TRANSCRIBING ---")
    
    if whisper_model is None:
        load_model()
        
    # faster-whisper accepts BinaryIO objects directly, avoiding disk writes
    segments, info = whisper_model.transcribe(audio_data, beam_size=5)
    
    full_text = "".join([segment.text for segment in segments])
        
    print(f"EDI heard: {full_text}")
    return full_text.strip()
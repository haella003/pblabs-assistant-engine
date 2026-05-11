import requests
import os
import sounddevice as sd
import numpy as np
import wave
import sys

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8080/chat"  # Update if your endpoint name is different
TEMP_AUDIO = "temp_recording.wav"
SAMPLE_RATE = 16000  # Standard for Whisper

def record_audio(duration=5):
    """Records audio from the mic and saves to a temp WAV file."""
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    with wave.open(TEMP_AUDIO, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(recording.tobytes())
    return TEMP_AUDIO

def send_to_edi(text=None, audio_path=None):
    """Sends either text or audio to your FastAPI backend."""
    try:
        if audio_path:
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{API_URL}/voice", files=files)
        else:
            response = requests.post(API_URL, json={"text": text})
            
        return response.json()
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def main():
    print("--- EDI TEST BENCH: TEXT OR VOICE ---")
    while True:
        mode = input("\nChoose Mode: [T]ext, [V]oice, or [Q]uit: ").lower()
        
        if mode == 'q':
            break
            
        if mode == 't':
            user_text = input("You (Type): ")
            data = send_to_edi(text=user_text)
            if data:
                print(f"EDI (Text): {data.get('response')}")
                # If your backend sends audio path, you could play it here
                
        elif mode == 'v':
            audio_file = record_audio()
            data = send_to_edi(audio_path=audio_file)
            if data:
                print(f"EDI (Transcribed): {data.get('user_text')}")
                print(f"EDI (Response): {data.get('response')}")
                # To hear the voice, your backend should be generating the .wav 
                # and this script can play it using 'os.system' or 'pygame'
                if data.get('audio_url'):
                    print("Playing EDI's voice...")
                    # Example for Mac:
                    os.system(f"afplay {data.get('audio_url')}")

if __name__ == "__main__":
    main()
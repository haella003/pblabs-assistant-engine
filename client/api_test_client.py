import requests
import sounddevice as sd
from scipy.io.wavfile import write
import base64
import os
import time
import numpy as np

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8080"
TEMP_WAV = "temp_voice_segment.wav" 
DEVICE_ID = 2 # MacBook Pro Microphone

def record_audio(duration=5, fs=44100):
    print(f"\nListening...")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=DEVICE_ID)
        sd.wait() 
        audio_int16 = (recording * 32767).astype('int16')
        write(TEMP_WAV, fs, audio_int16)
        return True
    except Exception as e:
        print(f"Recording Error: {e}")
        return False

def send_chat_audio():
    print("Processing...")
    try:
        # Convert audio to base64
        with open(TEMP_WAV, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # delete client WAV immediately after reading into memory
        if os.path.exists(TEMP_WAV):
            os.remove(TEMP_WAV)

        payload = {"audio_data": audio_base64, "generate_audio": False}
        response = requests.post(f"{BASE_URL}/chat/audio", json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            
            # Extract EDI's response and emotion
            edi_text = res_json.get('text', '...')
            edi_emotion = res_json.get('emotion', 'NEUTRAL')
            
            print("-" * 40)
            print(f"EDI [{edi_emotion}]: {edi_text}")
            print("-" * 40)
        else:
            print(f"Server Error: {response.status_code}")
    except Exception as e:
        print(f"Client Error: {e}")
    finally:
        if os.path.exists(TEMP_WAV):
            os.remove(TEMP_WAV)

def main():
    print("--- EDI VOICE-TO-TEXT CLIENT ---")
    
    # Start session
    try:
        requests.post(f"{BASE_URL}/session/start", json={"initial_emotion": "NEUTRAL"})
    except:
        print("Server not found. Make sure main.py is running.")
        return

    try:
        while True:
            val = input("\nPress Enter to speak, or 'q' to quit: ")
            if val.lower() == 'q': break
            if record_audio():
                send_chat_audio()
    finally:
        # End session and final cleanup of server-side file if visible
        requests.post(f"{BASE_URL}/session/end", json={"reason": "User exit"})
        if os.path.exists("last_user_voice.wav"):
            os.remove("last_user_voice.wav")

if __name__ == "__main__":
    main()
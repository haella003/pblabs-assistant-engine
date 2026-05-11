import requests
import sounddevice as sd
from scipy.io.wavfile import write
import base64
import os
import time
import numpy as np

# Attempt to load pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: 'pygame' not found. Audio responses will be saved but not played automatically.")

BASE_URL = "http://127.0.0.1:8080"
TEMP_WAV = "client_temp_mic.wav"
OUTPUT_WAV = "client_temp_response.wav"

def start_session():
    """Tests the POST /session/start endpoint"""
    print("\n[1/3] Initializing Session and Loading Models...")
    payload = {
        "initial_emotion": "NEUTRAL",
        "available_emotions": [
            {"name": "HAPPY", "description": "Joyful, energetic, and upbeat."},
        ]
    }
    try:
        response = requests.post(f"{BASE_URL}/session/start", json=payload)
        response.raise_for_status()
        print("Server Response:", response.json())
        return True
    except Exception as e:
        print("Failed to start session. Is the FastAPI server running?")
        print(f"Error: {e}")
        return False

def record_audio(duration=5, fs=44100):
    print(f"\n🎤 Recording for {duration} seconds... SPEAK NOW!")
    
    # 1. REPLACE THE ID: Change '0' to the number you found in sd.query_devices()
    device_id = 0  
    
    # 2. Record using float32 (the most stable format for macOS)
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=device_id)
    sd.wait() 
    
    # 3. Normalize and convert to 16-bit PCM for the WAV file
    audio_int16 = (recording * 32767).astype('int16')
    write(TEMP_WAV, fs, audio_int16)
    
    # 4. Final verification
    file_size = os.path.getsize(TEMP_WAV)
    print(f"✅ Recording saved: {file_size} bytes")
    
    if file_size < 1000:
        print("⚠️ WARNING: The recording file is nearly empty. Check your Mac mic settings!")
        
    return TEMP_WAV

def play_raw_audio(raw_bytes, fs=22050):
    """Plays raw PCM 16-bit Mono audio"""
    import numpy as np
    
    # 1. Convert bytes back to a numpy array (int16)
    audio_array = np.frombuffer(raw_bytes, dtype=np.int16)
    
    # 2. Use sounddevice to play the raw array directly
    print("Playing raw PCM response...")
    sd.play(audio_array, fs)
    sd.wait()

def send_chat_audio(filename):
    """Encodes audio to Base64 and sends as JSON to the /chat/audio endpoint"""
    print("Sending audio to server for transcription and LLM processing...")
    
    try:
        # 1. Read the audio file as binary
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        
        # 2. Encode binary to a Base64 string
        # This converts "wet" binary data into "dry" text safe for JSON
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # 3. Build the JSON payload to match your AudioChatRequest model
        payload = {
            "audio_data": audio_base64,
            "generate_audio": True
        }
        
        start_time = time.time()
        # 4. Use the 'json=' parameter to send it as application/json
        response = requests.post(f"{BASE_URL}/chat/audio", json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            print(f"DEBUG: Server returned: {res_json}")
            print(f"Response time: {time.time() - start_time:.2f}s")
            print(f"\nEDI [{res_json.get('emotion', 'NEUTRAL')}]: {res_json.get('text')}")
            
            # 5. Handle the EDI's voice response (Base64 -> File)
            b64_audio = res_json.get("audio_base64")
            if b64_audio:
                audio_bytes = base64.b64decode(b64_audio)
                with open(OUTPUT_WAV, "wb") as out_f:
                    out_f.write(audio_bytes)
                
                play_audio(OUTPUT_WAV)
            else:
                print("No audio data was returned from the server.")
        else:
            print(f"Server Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Client Error: {e}")
        
def end_session():
    """Tests the POST /session/end endpoint"""
    print("\n[3/3] Ending Session and Wiping Memory...")
    payload = {"reason": "User exited test client."}
    try:
        response = requests.post(f"{BASE_URL}/session/end", json=payload)
        print("Server Response:", response.json())
    except Exception as e:
        print("Failed to end session.")
        print(f"Error: {e}")

def main():
    print("=== EDI API TEST CLIENT ===")
    
    if not start_session():
        return
        
    try:
        while True:
            val = input("\n[2/3] Press Enter to record 5s of audio, or type 'q' to quit: ")
            if val.lower() == 'q':
                break
                
            record_audio()
            send_chat_audio(TEMP_WAV)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        end_session()
        
        # Cleanup temporary client files
        if os.path.exists(TEMP_WAV):
            os.remove(TEMP_WAV)
        if os.path.exists(OUTPUT_WAV):
            os.remove(OUTPUT_WAV)

if __name__ == "__main__":
    main()
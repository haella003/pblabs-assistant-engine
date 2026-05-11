import requests
import sounddevice as sd
from scipy.io.wavfile import write
import base64
import os
import time
import numpy as np

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8080"
TEMP_WAV = "client_temp_mic.wav"
OUTPUT_WAV = "client_temp_response.wav"
# Update this ID based on: python3 -c "import sounddevice as sd; print(sd.query_devices())"
DEVICE_ID = 1  

def start_session():
    """Initializes the session on the server"""
    print("\n[1/3] Initializing Session and Loading Models...")
    payload = {
        "initial_emotion": "NEUTRAL",
        "available_emotions": [{"name": "HAPPY", "description": "Upbeat"}]
    }
    try:
        response = requests.post(f"{BASE_URL}/session/start", json=payload, timeout=30)
        response.raise_for_status()
        print("✅ Server Response:", response.json())
        return True
    except Exception as e:
        print(f"❌ Connection Error: Is the server running at {BASE_URL}?")
        return False

def record_audio(duration=5, fs=44100):
    """Records audio and checks for silence"""
    #print(f"\n🎤 Recording for {duration} seconds... SPEAK NOW!")
    try:
        # Record in float32 for macOS stability
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32', device=DEVICE_ID)
        sd.wait() 
        
        # Check volume (Sanity check)
        max_val = np.max(np.abs(recording))
        if max_val < 0.01:
            print("⚠️ WARNING: Very low volume detected! Check your Mic input settings.")

        # Convert to 16-bit PCM for the WAV file
        audio_int16 = (recording * 32767).astype('int16')
        write(TEMP_WAV, fs, audio_int16)
        print(f"✅ Recording saved ({os.path.getsize(TEMP_WAV)} bytes)")
        return True
    except Exception as e:
        print(f"❌ Recording Error: {e}")
        return False

def play_audio(filename_or_bytes):
    """Plays audio data. Supports both filenames and raw bytes."""
    try:
        if isinstance(filename_or_bytes, bytes):
            # Play raw PCM bytes
            audio_array = np.frombuffer(filename_or_bytes, dtype=np.int16)
            sd.play(audio_array, samplerate=22050)
            sd.wait()
        elif os.path.exists(filename_or_bytes):
            # Play a WAV file using sounddevice (safer than pygame for raw data)
            import soundfile as sf
            data, fs = sf.read(filename_or_bytes)
            sd.play(data, fs)
            sd.wait()
    except Exception as e:
        print(f"❌ Playback Error: {e}")

def send_chat_audio():
    """Sends recorded audio to server and handles the response"""
    print("⏳ Processing...")
    try:
        with open(TEMP_WAV, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {"audio_data": audio_base64, "generate_audio": True}
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/chat/audio", json=payload)
        
        if response.status_code == 200:
            res_json = response.json()
            print(f"⏱  Response time: {time.time() - start_time:.2f}s")
            print(f"\nEDI [{res_json.get('emotion', 'NEUTRAL')}]: {res_json.get('text')}")
            
            # Handle Voice Response
            b64_audio = res_json.get("audio_base64")
            if b64_audio:
                audio_bytes = base64.b64decode(b64_audio)
                play_audio(audio_bytes)
            else:
                print("🔇 (No voice data returned)")
        else:
            print(f"❌ Server Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Client Error: {e}")

def main():
    print("=== EDI API TEST CLIENT ===")
    if not start_session(): return
        
    try:
        while True:
            val = input("\n[2/3] Press Enter to record (5s), or 'q' to quit: ")
            if val.lower() == 'q': break
                
            if record_audio():
                send_chat_audio()
    finally:
        # End session and clean up
        requests.post(f"{BASE_URL}/session/end", json={"reason": "User exit"})
        for f in [TEMP_WAV, OUTPUT_WAV]:
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    main()
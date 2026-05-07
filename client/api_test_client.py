import requests
import sounddevice as sd
from scipy.io.wavfile import write
import base64
import os
import time

# --- VR HEADSET INTERFACE TEST CLIENT ---

# Attempt to load pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: 'pygame' not found. Audio responses will be saved but not played automatically.")

# parameters
BASE_URL = "http://127.0.0.1:8080"
TEMP_WAV = "client_temp_mic.wav"
OUTPUT_WAV = "client_temp_response.wav"

# pre-check if server is running
def start_session():
    """Tests the POST /session/start endpoint"""
    print("\n[1/3] Initializing Session and Loading Models...")
    payload = {
        "initial_emotion": "NEUTRAL",
        "available_emotions": [
            {"name": "HAPPY", "description": "Joyful, energetic, and upbeat."},
            {"name": "BORED", "description": "Cold, logical, and precise."},
            {"name": "TENDERNESS", "description": "Empathetic, slow, and melancholic."}
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

# Ears
# press enter with computer to record 5 seconds of audio from the microphone
def record_audio(duration=5, fs=44100):
    """Records audio from the default microphone"""
    print(f"\nRecording for {duration} seconds... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait() # Block until recording is finished
    write(TEMP_WAV, fs, recording)
    print("Recording saved.")
    return TEMP_WAV

def play_audio(filename):
    """Plays the audio file using pygame"""
    if not PYGAME_AVAILABLE or not os.path.exists(filename):
        return
        
    print("Playing EDI's response...")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    pygame.mixer.quit()

# Messenger
# sends the recorded audio to the server and handles the response
# expects a JSON with 'text', 'emotion', and 'audio_base64' (string)
def send_chat_audio(filename):
    """Tests the POST /chat/audio endpoint"""
    print("Sending audio to server for transcription and LLM processing...")
    
    with open(filename, "rb") as f:
        # We send the audio file as multipart/form-data and generate_audio as Form data
        files = {"audio_file": (filename, f, "audio/wav")}
        data = {"current_emotion": "NEUTRAL"}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/process-voice", files=files, data=data)
        
    if response.status_code == 200:
        # 3. Get the Emotion from the 'envelope' (the Header)
        emotion = response.headers.get("X-EDI-Emotion", "NEUTRAL")
        print(f"\nEDI [{emotion}]: Response received.")

        # 4. Save the actual sound data to a file
        with open("edi_response.mp3", "wb") as out_f:
            out_f.write(response.content)
        
        # 5. Play the sound!
        play_audio("edi_response.mp3")
        
    else:
        print(f"Server Error: {response.status_code} - {response.text}")
        
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
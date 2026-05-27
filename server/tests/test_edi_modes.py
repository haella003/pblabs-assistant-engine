import base64
from json.tool import main
import requests
import os
import io
import sounddevice as sd
import soundfile as sf
import numpy
import wave

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8080/chat/audio"
TEMP_AUDIO = "temp_recording.wav"
SAMPLE_RATE = 16000

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

def play_audio(audio_bytes):
    """Plays audio bytes."""
    # Wrap bytes in a buffer so soundfile can read it like a file
    data, fs = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, fs)
    sd.wait()

def main():
    print("--- EDI TESTER ---")
    
    while True:
        mode = input("\n[V]oice Record, [T]ext Input, [Q]uit: ").lower()
        if mode == 'q': 
            break
        
        audio_b64 = ""
        text_query = ""
        
        # Determine if EDI should speak
        use_voice = input("Should EDI speak for this response? (y/n): ").lower() == 'y'

        if mode == 'v':
            record_audio()
            with open(TEMP_AUDIO, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode('utf-8')
        elif mode == 't':
            text_query = input("Type your question for EDI: ")
        else:
            continue

        payload = {
            "audio_data": audio_b64, # Empty if text mode
            "text_query": text_query, # Empty if voice mode
            "generate_audio": use_voice
        }

        try:
            print("Sending to EDI...")
            response = requests.post(API_URL, json=payload)
            data = response.json()

            if "text" in data:
                print(f"\nEDI [{data['emotion']}]: {data['text']}")
                
                # This check ensures we only play if the server actually sent audio
                if data.get("audio_base64"):
                    print("Playing response...")
                    audio_bytes = base64.b64decode(data["audio_base64"])
                    play_audio(audio_bytes)
                else:
                    # print("(Voice skipped as requested)")
                    pass
            else:
                print(f"Server Error: {data}")
        
        except Exception as e:
            print(f"Connection Failed: {e}")

if __name__ == "__main__":
    main()
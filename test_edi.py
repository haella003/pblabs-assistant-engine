import requests
import os

# The address of your start_edi.py server
URL = "http://127.0.0.1:8080"

def conversation():
    # 1. Start the session ONCE
    requests.post(f"{URL}/session/start", json={"initial_emotion": "NEUTRAL"})
    
    while True:
        input("\nPress Enter to send 'test_input.mp3'...")
        
        if os.path.exists("test_input.mp3"):
            print("--- Sending to Server... ---")
            with open("test_input.mp3", "rb") as f:
                # Use 'audio_file' to match the server's variable name
                files = {"audio_file": ("test_input.mp3", f, "audio/mpeg")}
                data = {"current_emotion": "NEUTRAL"}
                
                # THIS LINE MUST WAIT
                response = requests.post(f"{URL}/process-voice", files=files, data=data)

            if response.status_code == 200:
                emotion = response.headers.get("X-EDI-Emotion")
                print(f"Received Response! EDI Emotion: {emotion}")
                with open("edi_response.mp3", "wb") as f:
                    f.write(response.content)
                print(f"Saved to edi_response.mp3 ({os.path.getsize('edi_response.mp3')} bytes)")
            else:
                print(f"Server Error: {response.status_code} - {response.text}")
        else:
            print("File 'test_input.mp3' not found in folder!")
        
        cont = input("\nContinue conversation? (y/n): ")
        if cont.lower() == 'n':
            break
        
    # 4. End the session ONLY at the very end
    requests.post(f"{URL}/session/end", json={"reason": "User quit"})
    
if __name__ == "__main__":
    conversation()
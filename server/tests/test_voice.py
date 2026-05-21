import subprocess
import os

# Test the Piper TTS engine directly to ensure it's working before integrating into the main server.

# --- CONFIGURATION ---
PIPER_EXE = "venv/bin/piper"
MODEL_PATH = "server/piper_voices/en_US-amy-medium.onnx"
OUTPUT_WAV = "server/tests/test_voice_output.wav"

def test_voice():
    test_text = "This is a direct test of the Piper voice engine."
    
    # Ensure the model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}")
        return

    print(f"Synthesizing: '{test_text}'")
    
    # Command to run Piper directly
    command = f'echo "{test_text}" | {PIPER_EXE} --model {MODEL_PATH} --output_file {OUTPUT_WAV}'
    
    try:
        os.system(command)
        if os.path.exists(OUTPUT_WAV):
            print(f"Success! Created {OUTPUT_WAV}")
            os.system(f"afplay {OUTPUT_WAV}")
        else:
            print("Failed to create audio file.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_voice()
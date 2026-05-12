import subprocess
import os
import time

# --- CONFIGURATION ---
# 1. Path to your Piper binary (Check if this exists!)
PIPER_EXE = "../../venv/bin/piper" 
# 2. Path to your Model
MODEL_PATH = "../piper_voices/en_US-amy-medium.onnx"
# 3. Output file
OUTPUT_WAV = "test_output.wav"

test_text = "Hello! I am testing the voice engine on my new M 4 MacBook Pro."

def test_binary_synthesis():
    print(f"--- DIAGNOSTIC: Testing Binary at {PIPER_EXE} ---")
    
    if not os.path.exists(PIPER_EXE):
        print(f"❌ ERROR: Piper binary not found at {PIPER_EXE}")
        return

    # The command we would normally run in the terminal
    command = [
        PIPER_EXE,
        "--model", MODEL_PATH,
        "--output_file", OUTPUT_WAV
    ]

    try:
        print("Running Piper subprocess...")
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Send text and wait for result
        stdout, stderr = process.communicate(input=test_text)

        if os.path.exists(OUTPUT_WAV) and os.path.getsize(OUTPUT_WAV) > 0:
            print(f"✅ SUCCESS! Created {OUTPUT_WAV} ({os.path.getsize(OUTPUT_WAV)} bytes)")
            # Try to play it
            os.system(f"afplay {OUTPUT_WAV}")
        else:
            print("❌ FAILED: File is still empty or wasn't created.")
            print(f"Piper Error Output: {stderr}")

    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")

if __name__ == "__main__":
    test_binary_synthesis()
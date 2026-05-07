import os
import sys
import subprocess
import re

# 1. FIND THE PROJECT ROOT (Portable logic)
# This finds the 'EDI_Backend' folder regardless of where you run it
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# 2. DEFINE THE PATHS (Globally, so the functions can see them)
# This points to your Amy model
MODEL_PATH = os.path.join(BASE_DIR, "server", "piper_voices", "en_US-amy-medium.onnx")

# This finds the piper binary inside your virtual environment
PIPER_CMD = os.path.join(sys.prefix, "bin", "piper")

# If the venv path doesn't exist, fallback to the global command
if not os.path.exists(PIPER_CMD):
    PIPER_CMD = "piper"

def generate_speech(text, output_file="test_output.wav"):
    # Clean the [EMOTION] tags
    clean_text = re.sub(r"\[.*?\]", "", text).strip()
    
    # We build the command using the global variables defined above
    command = f'echo "{clean_text}" | {PIPER_CMD} --model "{MODEL_PATH}" --output_file "{output_file}"'
    
    try:
        # Check if the model actually exists to avoid cryptic errors
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Error: Model not found at: {MODEL_PATH}")
            return

        subprocess.run(command, shell=True, check=True)
        print(f"✅ Success! Audio saved to: {os.path.abspath(output_file)}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during synthesis: {e}")

if __name__ == "__main__":
    test_text = "I am now using relative paths, so I can run on any computer!"
    generate_speech(test_text)
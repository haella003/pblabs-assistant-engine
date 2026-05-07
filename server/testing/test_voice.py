import os
import subprocess
import re

# UNIVERSAL PATH SETUP
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR)) 
MODEL_PATH = os.path.join(BASE_DIR, "server", "piper_voices", "en_US-amy-medium.onnx")

# Use "piper", as long as piper is installed via pip, the system will find it
PIPER_CMD = "piper" 

def generate_speech(text, output_file="test_output.wav"):
    # Strip the [EMOTION] tags
    clean_text = re.sub(r"\[.*?\]", "", text).strip()
    
    # uses a list for subprocess.run for better security and cross-platform support
    command = f'echo "{clean_text}" | {PIPER_CMD} --model "{MODEL_PATH}" --output_file "{output_file}"'
    
    try:
        # ensures the model file actually exists before trying to run
        if not os.path.exists(MODEL_PATH):
            print(f"Error: Model not found at {MODEL_PATH}")
            return

        subprocess.run(command, shell=True, check=True)
        print(f"Success! Audio saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during synthesis: {e}")

# Test
if __name__ == "__main__":
    generate_speech("I am now using relative paths, so I can run on any computer!")
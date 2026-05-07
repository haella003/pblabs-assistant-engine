import os
import subprocess
import re

# This finds the absolute path to your EDI_Backend folder automatically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Now the paths are "bulletproof"
PIPER_PATH = os.path.join(BASE_DIR, "piper_voices", "piper") 
MODEL_PATH = os.path.join(BASE_DIR, "piper_voices", "models", "en_GB-southern_english_female-low.onnx")

def synthesize(text, output_path="response.wav"):
    """
    Generates high-quality local speech using Piper.
    """
    # Clean the text of emotion tags [HAPPY] etc.
    clean_text = re.sub(r"\[.*?\]", "", text).strip()
    
    print(f"Piper Logic: Generating speech for -> {clean_text[:30]}...")

    # The command to run Piper
    command = f'echo "{clean_text}" | {PIPER_PATH} --model {MODEL_PATH} --output_file {output_path}'
    
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Piper Error: {e}")
        return False
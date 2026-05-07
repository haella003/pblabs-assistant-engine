import os
import subprocess
import re

# Update these paths to where your files actually are!
PIPER_PATH = "./server/piper_voices/piper" 
MODEL_PATH = "./server/piper_voices/models/en_GB-southern_english_female-low.onnx"

def synthesize(text, output_path="response.wav"):
    """
    Generates high-quality local speech using Piper.
    Replaces the old gTTS cloud-based system.
    """
    # 1. Strip the emotion tags like [HAPPY] so EDI doesn't literally say "Bracket Happy"
    clean_text = re.sub(r"\[.*?\]", "", text).strip()
    
    print(f"Piper Logic: Generating speech for -> {clean_text[:30]}...")

    # 2. Build the command
    # We use 'quoted' text to handle spaces and special characters safely
    command = f'echo "{clean_text}" | {PIPER_PATH} --model {MODEL_PATH} --output_file {output_path}'
    
    try:
        # 3. Run Piper
        subprocess.run(command, shell=True, check=True, capture_output=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"Success: Piper created {output_path}")
            return True
        else:
            print("Piper failed: Audio file is empty or missing.")
            return False
            
    except Exception as e:
        print(f"Error in Piper Synthesis: {e}")
        return False
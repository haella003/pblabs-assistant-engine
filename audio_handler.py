from gtts import gTTS
import os

def synthesize(text, output_path):
    """
    Creates a real MP3 file using Google TTS.
    Includes a check to make sure the file isn't empty!
    """
    print(f"Audio Logic: Generating speech for -> {text[:30]}...")
    
    try:
        # 1. Clear any old 25-byte file first
        if os.path.exists(output_path):
            os.remove(output_path)
            
        # 2. Generate the speech
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        
        # 3. VERIFICATION: Check the size
        file_size = os.path.getsize(output_path)
        if file_size < 100:
            print(f"Warning: File {output_path} is too small ({file_size} bytes).")
        else:
            print(f"Success: Created MP3 ({file_size} bytes)")
            
    except Exception as e:
        print(f"Error in gTTS: {e}")
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu")

def transcribe(audio_path):
    # This is an "AI Process" - it takes a file, returns text.
    segments, _ = model.transcribe(audio_path)
    return "".join([s.text for s in segments])
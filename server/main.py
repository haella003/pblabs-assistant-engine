from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import base64
import datetime
import asyncio
import io
import os

from server.handler import audio_handler
from server.handler import speech_handler
from server.handler import llm_handler
from server.handler.logger_handler import save_chat_log

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Added status tracking for the client to poll
session_state = {
    "is_active": False,
    "session_id": "",
    "emotion_rules": "",
    "status": "offline",
    "current_emotion": "NEUTRAL"
}

class EmotionDef(BaseModel):
    name: str
    description: str
    
class StartRequest(BaseModel):
    initial_emotion: str = "NEUTRAL"
    available_emotions: List[EmotionDef] = []

class EndRequest(BaseModel):
    reason: str

class AudioChatRequest(BaseModel):
    audio_data: str
    generate_audio: bool = False

@app.get("/status")
def get_status():
    """Endpoint for the client to poll EDI's current state."""
    return {
        "is_active": session_state["is_active"],
        "status": session_state["status"],
        "current_emotion": session_state["current_emotion"]
    }

@app.post("/session/start")
def start_session(request: StartRequest):
    session_state["is_active"] = True
    session_state["status"] = "booting"
    session_state["session_id"] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    rules = "\nIMPORTANT - You must start your response with one of these emotion tags based on these rules:\n"
    for e in request.available_emotions:
        rules += f"- {e.name}: {e.description}\n"
    rules += "Format: [EMOTION_NAME] | your message here."
    session_state["emotion_rules"] = rules

    print("API: Booting up EDI models...")
    audio_handler.load_model()
    speech_handler.load_model()
    
    # Preload LLM into memory
    llm_handler.preload_model()
    llm_handler.reset_memory()
    
    session_state["status"] = "idle"
    return {
        "status": "started",
        "description": "Models loaded into memory. EDI is ready."
    }

@app.post("/session/end")
def end_session(request: EndRequest):
    session_state["is_active"] = False
    session_state["status"] = "offline"
    print(f"API: Session ended. Reason: {request.reason}. Unloading models...")
    
    llm_handler.reset_memory()
    
    # Unload all models from memory
    llm_handler.unload_model()
    audio_handler.unload_model()
    speech_handler.unload_model()
    
    return {"message": f"EDI session closed successfully. Memory wiped."}

@app.post("/chat/audio")
async def chat_with_audio(request: AudioChatRequest):
    if not session_state["is_active"]:
        return {"error": "Session is not active. Call /session/start first."}
        
    session_id = session_state["session_id"]
    timestamp = datetime.datetime.now().strftime("%H-%M-%S")
    os.makedirs("logs", exist_ok=True)
    
    # 1. Decode the Base64 string directly into RAM
    try:
        # 1. Decode the Base64 string back into real bytes
        audio_bytes = base64.b64decode(request.audio_data)
        temp_input = f"logs/input_{timestamp}.wav"
        
        # 2. SAVE to a temporary file (Whisper is much happier with files)
        temp_input = "logs/last_user_voice.wav"
        with open(temp_input, "wb") as f:
            f.write(audio_bytes)
            
    except Exception as e:
        print(f"Decoding Error: {e}")
        return {"error": "Failed to decode audio data"}, 400

    # 3. Transcribe using the FILE PATH
    session_state["status"] = "transcribing"
    # Pass the path string "logs/last_user_voice.wav"
    user_text = await asyncio.to_thread(audio_handler.transcribe_audio, temp_input)
    if not user_text:
        return JSONResponse(
        status_code=500,
        content={"text": "", "emotion": "NEUTRAL", "message": "Failed to transcribe audio"}
    )
        
    # 3. Formulate LLM Response
    session_state["status"] = "thinking"
    full_prompt = user_text + session_state["emotion_rules"]
    raw_response = await asyncio.to_thread(llm_handler.get_edi_response, full_prompt)
    
    if "|" in raw_response:
        parts = raw_response.split("|", 1)
        emotion = parts[0].replace("[", "").replace("]", "").strip()
        message = parts[1].strip()
    else:
        emotion = "NEUTRAL"
        message = raw_response

    session_state["current_emotion"] = emotion

    # Log EDI response
    await asyncio.to_thread(save_chat_log, "EDI", message, emotion, session_id)

    # 4. Generate Voice in Memory (Optional)
    audio_base64 = None
    if request.generate_audio:  # Updated to use request property
        session_state["status"] = "generating_audio"
        wav_bytes = await asyncio.to_thread(speech_handler.generate_speech, message)
        if wav_bytes:
            audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
            
            # --- Save generated audio to disk for evaluation ---
            edi_audio_path = f"logs/{session_id}_{timestamp}_edi.wav"
            with open(edi_audio_path, "wb") as f:
                f.write(wav_bytes)

    # 5. Return JSON payload and reset to idle
    session_state["status"] = "idle"
    return {
        "text": message,
        "emotion": emotion,
        "audio_base64": audio_base64
    }

if __name__ == "__main__":
    # Remove the string "main:app" and the reload=True (direct objects don't support reload)
    uvicorn.run(app, host="127.0.0.1", port=8080)
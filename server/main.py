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
import fitz

from handler import audio_handler
from handler import speech_handler
from handler import llm_handler
from handler import knowledge_handler
from handler.logger_handler import save_chat_log
from handler.speech_handler import generate_speech

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration path for knowledge vector indexing
KNOWLEDGE_PATH = os.path.join("server", "knowledge_vault")

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
    audio_data: Optional[str] = ""
    text_query: Optional[str] = ""
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
    knowledge_handler.build_knowledge_index(KNOWLEDGE_PATH)
    
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
    user_text = ""
    temp_input = "logs/last_user_voice.wav"
    os.makedirs("logs", exist_ok=True)

    # --- 1. ROUTE INPUT: TEXT OR AUDIO ---
    if request.text_query:
        # User typed their question
        user_text = request.text_query
        print(f"Received Text Input: {user_text}")
    else:
        # User sent audio data
        try:
            audio_bytes = base64.b64decode(request.audio_data)
            with open(temp_input, "wb") as f:
                f.write(audio_bytes)
            
            session_state["status"] = "transcribing"
            user_text = await asyncio.to_thread(audio_handler.transcribe_audio, temp_input)
            
            # Cleanup audio file immediately after transcribing
            if os.path.exists(temp_input): os.remove(temp_input)
        except Exception as e:
            print(f"Decoding Error: {e}")
            return JSONResponse(status_code=400, content={"error": "Failed to decode audio data"})

    if not user_text:
        return {"text": "", "emotion": "NEUTRAL", "message": "No input detected"}
    
    # Log User Input
    await asyncio.to_thread(save_chat_log, "User", user_text, "NEUTRAL", session_id)
        
    # --- 2. FORMULATE LLM RESPONSE ---
    session_state["status"] = "thinking"
   
    # It will automatically fetch the persona, system rules, template, and context files.
    try:
        raw_response = await asyncio.to_thread(llm_handler.get_edi_response, user_text)
    except Exception as e:
        return {"error": f"LLM generation failed: {e}"}
    
    # Parse Emotion and Message
    if "|" in raw_response:
        parts = raw_response.split("|", 1)
        emotion = parts[0].replace("[", "").replace("]", "").strip()
        message = parts[1].strip()
    else:
        emotion, message = "NEUTRAL", raw_response

    # --- 3. SAVE STATE & SYSTEM LOGS ---
    session_state["current_emotion"] = emotion
    await asyncio.to_thread(save_chat_log, "EDI", message, emotion, session_id)

    # --- 4. GENERATE VOICE ---
    audio_base64 = None
    if request.generate_audio:
        print(f"--- STARTING AUDIO GENERATION FOR: {emotion} ---")
        wav_bytes = await asyncio.to_thread(speech_handler.generate_speech, message)
        if wav_bytes:
            audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
    
    session_state["status"] = "idle"
    return {
        "text": message,
        "emotion": emotion,
        "audio_base64": audio_base64,
        "user_text": user_text # Useful for debugging!
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
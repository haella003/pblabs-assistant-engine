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
from handler.logger_handler import save_chat_log
from handler.speech_handler import generate_speech

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# At the top of main.py
PERSONA_PATH = os.path.join("server", "personas", "EDI_Bachelorthesis.txt")
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

    # 1. Decode Audio
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        temp_input = "logs/last_user_voice.wav"
        with open(temp_input, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        print(f"Decoding Error: {e}")
        return JSONResponse(status_code=400, content={"error": "Failed to decode audio data"})

    # 2. Transcribe
    session_state["status"] = "transcribing"
    user_text = await asyncio.to_thread(audio_handler.transcribe_audio, temp_input)
    
    if not user_text:
        if os.path.exists(temp_input): os.remove(temp_input)
        return {"text": "", "emotion": "NEUTRAL", "message": "No speech detected"}
    
    await asyncio.to_thread(save_chat_log, "User", user_text, "NEUTRAL", session_id)
        
    # 3. Formulate LLM Response with Persona File
    session_state["status"] = "thinking"
    
    # a. Load the Persona
    with open(PERSONA_PATH, "r") as f:
        persona_content = f.read()
        
    # b. Load the specific Knowledge folder (Everything inside)
    knowledge_content = ""
    if os.path.exists(KNOWLEDGE_PATH) and os.path.isdir(KNOWLEDGE_PATH):
        for filename in os.listdir(KNOWLEDGE_PATH):
            file_path = os.path.join(KNOWLEDGE_PATH, filename)
            
            # Read Text Files
            if filename.endswith(".txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        knowledge_content += f"\n--- Source: {filename} ---\n{f.read()}\n"
                except: pass
            
            # Read PDF Files
            elif filename.endswith(".pdf"):
                try:
                    doc = fitz.open(file_path)
                    pdf_text = "".join([page.get_text() for page in doc])
                    knowledge_content += f"\n--- Source: {filename} ---\n{pdf_text}\n"
                    doc.close()
                except Exception as e:
                    print(f"Could not read PDF {filename}: {e}")
    
    if not knowledge_content:
        knowledge_content = "No specific data found in the vault."

   # c. Combine them into the prompt
    full_prompt = (
        f"SYSTEM INSTRUCTIONS:\n{persona_content}\n\n"
        f"KNOWLEDGE CONTEXT:\n{knowledge_content}\n\n"
        f"USER INPUT: {user_text}\n"
        f"{session_state['emotion_rules']}\n"
        f"5. LIMIT: Use exactly one or two short sentences."
    )
    
    raw_response = await asyncio.to_thread(llm_handler.get_edi_response, full_prompt)
    
    # Parse Emotion and Message
    if "|" in raw_response:
        parts = raw_response.split("|", 1)
        emotion = parts[0].replace("[", "").replace("]", "").strip()
        message = parts[1].strip()
    else:
        emotion = "NEUTRAL"
        message = raw_response

    session_state["current_emotion"] = emotion
    
    await asyncio.to_thread(save_chat_log, "EDI", message, emotion, session_id)

    # 4. Generate & Play Voice (FORCED FOR TESTING)
    audio_base64 = None
    wav_bytes = await asyncio.to_thread(speech_handler.generate_speech, message)
    
    # Check if the client set generate_audio to True
    if request.generate_audio:
        print(f"--- STARTING AUDIO GENERATION FOR: {emotion} ---")
        wav_bytes = await asyncio.to_thread(speech_handler.generate_speech, message)
        
        if wav_bytes:
            audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
            print(f"Audio encoded: {len(audio_base64)} characters")
    else:
        print("⏭Skipping audio generation (generate_audio=False)")
    
    # 5. Return JSON payload
    session_state["status"] = "idle"
    return {
        "text": message,
        "emotion": emotion,
        "audio_base64": audio_base64
    }

if __name__ == "__main__":
    # Remove the string "main:app" and the reload=True (direct objects don't support reload)
    # change host an port accordingly
    uvicorn.run(app, host="127.0.0.1", port=8080) 
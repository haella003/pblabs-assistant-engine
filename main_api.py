from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import time
import asyncio

app = FastAPI()

# Models
class EmotionDef(BaseModel):
    name: str
    description: str

class StartRequest(BaseModel):
    initial_emotion: str = "NEUTRAL"
    available_emotions: List[EmotionDef] = []

class EndRequest(BaseModel):
    reason: str

# start_edi.py will set this
shared_state = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "EDI API is Active"}

# --- START SESSION ---
@app.post("/session/start")
def start_session(request: StartRequest):
    if shared_state is not None:
        print(f"API: Session started. Emotion: {request.initial_emotion}")
        shared_state["status"] = "idle"
        shared_state["emotion"] = request.initial_emotion
        shared_state["session_active"] = True
        return {"status": "ready"}
    return {"error": "Shared state not initialized"}

# --- PROCESS VOICE (The Waiter) ---
@app.post("/process-voice")
async def process_voice(audio_file: UploadFile = File(...), current_emotion: str = Form("NEUTRAL")):
    print("API: Received voice file. Waking up the Brain...")
    
    # 1. Save the incoming file
    input_path = "incoming_voice.mp3"
    with open(input_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)

    # 2. Tell the Brain to start
    shared_state["message"] = input_path
    shared_state["emotion"] = current_emotion
    shared_state["status"] = "processing"
    
    # 3. THE WAIT LOOP
    max_wait = 20  
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # We use .get() to be safe
        if shared_state.get("status") == "completed":
            print("API: Brain finished! Sending response back.")
            output_path = shared_state.get("message")
            final_emotion = shared_state.get("emotion", "NEUTRAL")
            
            shared_state["status"] = "idle" # Reset for next turn
            
            return FileResponse(
                output_path, 
                media_type="audio/mpeg", 
                headers={"X-EDI-Emotion": final_emotion}
            )
        # Use asyncio.sleep so the API doesn't freeze
        await asyncio.sleep(0.5) 
    
    shared_state["status"] = "idle"
    return {"error": "The Brain took too long to respond."}

# --- END SESSION ---
@app.post("/session/end")
def end_session(request: EndRequest):
    if shared_state is not None:
        print(f"API: Ending session. Reason: {request.reason}")
        shared_state["session_active"] = False
        shared_state["status"] = "idle"
        return {"status": "ended"}
    return {"error": "Shared state not initialized"}
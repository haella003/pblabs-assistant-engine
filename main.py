import time
import os
import datetime
import speech_handler  
import audio_handler   
import llm_handler

def get_edi_answer(user_text, emotion_rules_text=""):
    """Takes text, asks the LLM, and returns (message, emotion)"""
    full_prompt = user_text + emotion_rules_text
    # This calls the LLM (GPT/Ollama)
    raw_response = llm_handler.get_edi_response(full_prompt)
    
    if "|" in raw_response:
        parts = raw_response.split("|", 1)
        emotion = parts[0].replace("[", "").replace("]", "").strip()
        message = parts[1].strip()
    else:
        emotion = "NEUTRAL"
        message = raw_response
        
    return message, emotion

def run_edi_loop(shared_data):
    print("EDI SYSTEM ONLINE (HEADLESS SERVER MODE).")
    
    while True:
        try:
            # 1. CHECK FOR MEMORY WIPE
            if shared_data.get("reset_memory"):
                print("Main: Resetting memory...")
                llm_handler.reset_memory()
                shared_data["reset_memory"] = False
                continue

            # 2. WAIT FOR THE API TO GIVE US A FILE
            # We only act when status is "processing"
            if shared_data.get("status") == "processing":
                
                # Retrieve info from the shared whiteboard
                input_audio_path = shared_data.get("message") # e.g. "incoming_voice.mp3"
                detected_emotion = shared_data.get("emotion", "NEUTRAL")
                session_id = shared_data.get("session_id", "default")

                print(f"Main: Received file {input_audio_path}. Processing...")

                # 3. TRANSCRIBE (Whisper)
                # Instead of record_audio(), we read the file saved by the API
                user_text = speech_handler.transcribe(input_audio_path)
                
                if not user_text or not user_text.strip():
                    shared_data["status"] = "idle"
                    continue

                print(f"User said: {user_text}")
                # save_chat_log("User", user_text, "NEUTRAL", session_id)

                # 4. THINKING PHASE (LLM + RAG)
                shared_data["status"] = "thinking"
                
                # emotion rules
                emotion_rules_text = "\nFormat: [EMOTION] | message" 
                
                message, emotion = get_edi_answer(user_text, emotion_rules_text)

                # 5. SYNTHESIZE (Piper TTS)
                # Instead of speak(), we save to a file
                output_audio_path = f"response_{session_id}.mp3"
                
                # IMPORTANT: Update your Piper call to 'synthesize_to_file'
                audio_handler.synthesize(message, output_audio_path)
                
                # Wait until the file is actually on the disk and has data
                timeout = 5  # seconds
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 100:
                        print(f"Main: Audio confirmed ({os.path.getsize(output_audio_path)} bytes)")
                        break
                    time.sleep(0.2)

                # 6. HAND BACK TO API
                shared_data["message"] = output_audio_path
                shared_data["emotion"] = emotion
                shared_data["status"] = "completed" # This tells the API to send the file back
                
                print(f"Main: Finished. Response saved to {output_audio_path}")
                # save_chat_log("EDI", message, emotion, session_id)

            # Keep the CPU from maxing out
            time.sleep(0.1)

        except Exception as e:
            print(f"Error in Brain Loop: {e}")
            time.sleep(2)
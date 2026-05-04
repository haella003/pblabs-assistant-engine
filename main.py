import time
import datetime
from audio_handler import record_audio, transcribe_audio
import llm_handler
from logger_handler import save_chat_log
from speech_handler import speak

# for chat_with_edi.py to get answer without running the whole loop
def get_edi_answer(user_text, emotion_rules_text=""):
    """Takes text, asks the LLM, and returns (message, emotion)"""
    full_prompt = user_text + emotion_rules_text
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
    print("EDI SYSTEM ONLINE. WAITING FOR SESSION TO START...")
    first_run = True
    session_id = "default"

    while True:
        try:
            # 0. CHECK FOR MEMORY WIPE FROM API
            if shared_data.get("reset_memory"):
                print(f"Main: API triggered memory wipe! Reason: {shared_data.get('end_reason')}")
                llm_handler.reset_memory() # Clear the sliding window
                shared_data["reset_memory"] = False
                first_run = True # Reset this so the next user gets a fresh session ID
                continue # Skip the rest of the loop and wait for the new user
            
            # 1. CHECK THE SHARED WHITEBOARD
            if not shared_data.get("session_active"):
                shared_data["status"] = "idle"
                shared_data["emotion"] = "NEUTRAL"
                first_run = True
                time.sleep(1)
                continue
            
            # HELPER: Build emotion rules from frontend
            emotions_list = shared_data.get("available_emotions", [])
            emotion_rules_text = ""
            
            if emotions_list:
                emotion_rules_text = "\n\IMPORTANT - You must start your reponse with one of these emotion tags based on these rules:\n"
                for emotion in emotions_list:
                    emotion_rules_text += f"- {emotion['name']}: {emotion['description']}\n"
                emotion_rules_text += "Format: [EMOTION_NAME] | your message here."
            
            # 2. GREETING LOGIC
            if shared_data.get("trigger_first_speech"):
                if first_run:
                    session_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    first_run = False
                
                shared_data["status"] = "thinking"
                print(f"Main: API triggered first speech! Waking up EDI")
                
                intro_prompt = "The user has just arrived at your station. Greet them energetically and welcome them to the PB Lab!"
                
                # Inject the emotion rules into the greeting prompt
                intro_prompt += emotion_rules_text
                raw_response = llm_handler.get_edi_response(intro_prompt)
                
                # Parse emotion
                if "|" in raw_response:
                    parts = raw_response.split("|", 1)
                    shared_data["emotion"] = parts[0].replace("[", "").replace("]", "").strip()
                    shared_data["message"] = parts[1].strip()
                else:
                    shared_data["emotion"] = "NEUTRAL"
                    shared_data["message"] = raw_response
                    
                shared_data["status"] = "speaking"
                print(f"EDI: {shared_data['message']}")
                save_chat_log("EDI", shared_data["message"], shared_data["emotion"], session_id)
                speak(shared_data["message"])
                
                # Turn off the flag so he doesn't repeat the intro forever
                shared_data["trigger_first_speech"] = False
                continue # Jump back to the start of the loop to enter listening phase 
            
            # 3. LISTENING PHASE
            shared_data["status"] = "listening"
            print("\n--- EDI IS LISTENING ---")
            
            audio_file = record_audio()
            user_text = transcribe_audio(audio_file)
            
            # guard against empty input
            if not user_text or not user_text.strip():
                # print("Main: Nothing heard or typed. Restarting loop...")
                continue
            
            clean_input = user_text.lower().strip()
            # print(f"User: {user_text}")
            save_chat_log("User", user_text, "NEUTRAL", session_id)

            # THE GOODBYE/POWER OFF GUARD
            # This triggers the "End" for the frontend without yapping
            shutdown_triggers = ["goodbye", "bye", "power off", "power of", "go now", "stop session", "by any", "shut down", "shut off", "end session", "end now"]
            
            if any(trigger in clean_input for trigger in shutdown_triggers):
                print("Main: Shutdown Trigger Detected!")
                
                # short silent signal or a very quick goodbye
                shared_data["emotion"] = "TENDERNESS"
                shared_data["message"] = "Shutting down. Goodbye!"
                
                shared_data["status"] = "speaking"
                speak(shared_data["message"])
                
                # This is what Frontend is waiting for to "end the game"
                shared_data["session_active"] = False
                shared_data["status"] = "idle"
                shared_data["reset_memory"] = True
                
                print("Main: Session ended. Shared state updated for Frontend.")
                continue # Skip the rest and wait for a new session
            
            # 4. THINKING PHASE
            shared_data["status"] = "thinking"
            
            # Use our new brain function here too!
            message, emotion = get_edi_answer(user_text, emotion_rules_text)
            
            shared_data["message"] = message
            shared_data["emotion"] = emotion
            shared_data["status"] = "speaking"
            
            save_chat_log("EDI", shared_data["message"], shared_data["emotion"], session_id)
            speak(shared_data["message"])
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

# --- THE GATEKEEPER ---
if __name__ == "__main__":
    # This block ONLY runs if you do 'python3 main.py'
    # It will NOT run when chat_with_edi.py imports this file.
    # Since shared_data comes from your Manager/API, you'd usually 
    # run this via start_edi.py anyway.
    print("Main.py launched directly. Waiting for API instructions...")
import os
import datetime

def log_conversation(role, text, emotion, session_id="default"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {role} ({emotion}): {text}\n"
    
    # Save to a folder called 'logs'
    os.makedirs("logs", exist_ok=True)
    filename = f"logs/chat_{session_id}.txt"
    
    with open(filename, "a") as f:
        f.write(log_entry)
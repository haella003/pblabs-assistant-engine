import os
import datetime

def save_chat_log(sender, message, emotion, session_id):
    os.makedirs("logs", exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"logs/Session_{date_str}.txt"
    
    with open(filename, "a", encoding="utf-8") as f:
        if sender == "EDI":
            # Format: [14:30:01] EDI [HAPPY]: Hello!
            f.write(f"[{timestamp}] EDI [{emotion.upper()}]: {message}\n")
        else:
            # Format: [14:30:00] User: Hi there
            f.write(f"[{timestamp}] User: {message}\n")
    
    return filename
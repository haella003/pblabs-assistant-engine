import os
import datetime

def save_chat_log(sender, message, emotion, session_id):
    # automatically creates a logs folder if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # set up timestamp and filename
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    filename = f"logs/Session_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt" # saves history and data
    
    # save log differently
    with open(filename, "a", encoding="utf-8") as f:
              if sender == "EDI":
                  f.write(f"[{timestamp}] EDI [{emotion}]: {message}\n")
              else:
                    f.write(f"[{timestamp}] User: {message}\n")
    
    return filename
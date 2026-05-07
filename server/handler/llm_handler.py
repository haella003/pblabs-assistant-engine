import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
import fitz # PyMuPDF

load_dotenv() 

client = OpenAI(
    base_url="http://localhost:11434/v1",  
    api_key="ollama",                     
)

chat_history = []

# knowledge base
def get_pdf_content(user_input):
    vault_path = "knowledge_vault"
    relevant_text = ""
    
    # We create a list of "keywords" from the user's question
    # We ignore small words like 'the', 'is', 'at'
    keywords = [word.lower() for word in user_input.split() if len(word) > 3]

    if not os.path.exists(vault_path):
        return ""

    for filename in os.listdir(vault_path):
        if filename.endswith(".pdf"):
            try:
                doc = fitz.open(os.path.join(vault_path, filename))
                for page in doc:
                    page_text = page.get_text()
                    
                    # If the user's question keywords are on this page, keep it!
                    if any(kw in page_text.lower() for kw in keywords):
                        relevant_text += f"\n--- Page {page.number} ---\n" + page_text
                        
                        # Stop if we hit 8000 chars (plenty for Gemma to read)
                        if len(relevant_text) > 8000:
                            break
                doc.close()
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
                
    return relevant_text

def get_relevant_knowledge(user_input):
    text = user_input.lower()
    combined_info = ""
    
    # --- 1. JSON KNOWLEDGE BASE LOGIC ---
    json_path = os.path.join("knowledge_vault", "knowledge.json")
    try:
        with open(json_path, "r") as file:
            knowledge_base = json.load(file)
    except FileNotFoundError:
        knowledge_base = {}

    found_keywords = []
    for category_name, package_data in knowledge_base.items():
        if category_name == "default":
            continue
        for keyword in package_data.get("keywords", []):
            if keyword in text:
                found_keywords.append(category_name)
                combined_info += f"FACT ({category_name}): {package_data['info']}\n"
    
    # Add default lab rules if any matches were found
    if found_keywords:
        default_info = knowledge_base.get("default", {}).get("info", "")
        combined_info = f"GENERAL LAB RULES: {default_info}\n\n" + combined_info
    
    # --- 2. SMART PDF SEARCH LOGIC ---
    # Pass user_input here so the search knows what to look for!
    pdf_info = get_pdf_content(user_input) 
    
    if pdf_info:
        # We removed [:2000]! The smart search already limits it to 8000 relevant chars.
        combined_info += f"\nRELEVANT EXCERPTS FROM THESIS:\n{pdf_info}"
        
    return combined_info

def load_persona(persona_path=None): # Added 'persona_path=None' here
    persona_folder = "personas"
    
    # If the folder doesn't exist, create it so the script doesn't crash
    if not os.path.exists(persona_folder):
        os.makedirs(persona_folder)

    # 1. If a specific path was provided, try to load that first
    if persona_path and os.path.exists(persona_path):
        with open(persona_path, "r") as f:
            return f.read()

    # 2. Otherwise, look for any .txt file in the personas folder
    for file in os.listdir(persona_folder):
        if file.endswith(".txt"):
            with open(os.path.join(persona_folder, file), "r") as f:
                return f.read()
                
    return "You are a helpful assistant." # Final fallback
    
# main response logic
def get_edi_response(user_input):
    global chat_history
    
    current_package = get_relevant_knowledge(user_input)
    base_instructions = load_persona("EDI_RZ_1.txt")
    
    system_prompt = f"""
    {base_instructions}
    
    CURRENT CONTEXT/KNOWLEDGE:
    {current_package}"""
    
    chat_history.append({"role": "user", "content": user_input})
    
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
        
    messages_to_send = [{"role": "system", "content": system_prompt}] + chat_history
    
    try:
        completion = client.chat.completions.create(
            model="gemma3:4b",
            messages=messages_to_send,
            max_tokens=150
        )
        
        response_text = completion.choices.message.content

        # --- EMOTION GUARDRAIL START ---
        APPROVED_EMOTIONS = ["AMAZED", "HAPPY", "CURIOUS", "CHEERFUL", "DISTRACTIBLE", "BORED", "TENDERNESS"]
        
        # This looks for the first word inside brackets, e.g., [HAPPY]
        match = re.search(r"\[([A-Za-z]+)\]", response_text)
        
        if match:
            detected_emotion = match.group(1).upper()
            if detected_emotion not in APPROVED_EMOTIONS:
                # If it's a weird emotion, swap the tag for [NEUTRAL]
                response_text = re.sub(r"\[[A-Za-z]+\]", "[NEUTRAL]", response_text, count=1)
        else:
            # If the LLM forgot brackets entirely, prepended [NEUTRAL]
            response_text = f"[NEUTRAL] {response_text}"
        # --- EMOTION GUARDRAIL END ---
        
        chat_history.append({"role": "assistant", "content": response_text})
        return response_text
        
    except Exception as e:
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history.pop()
        return f"[SORRY] | Brain Error: {str(e)}"

def reset_memory():
    """Wipes EDI's short-term memory clean for the next session."""
    global chat_history
    chat_history = []
    print("API Triggered: EDI'smemory has been completely wiped.")
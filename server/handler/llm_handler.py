import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2

load_dotenv() 

# Ensure this matches the model used in get_edi_response
MODEL_NAME = "gemma3:4b"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

PERSONA_PATH = "server/personas/EDI_RZ_1.txt"

client = OpenAI(
    base_url="http://localhost:11434/v1",  
    api_key="ollama",                     
)

chat_history = []

def preload_model():
    """Forces Ollama to load the model into memory AND warms up the inference engine."""
    print("--- LOADING & WARMING UP LLM MODEL ---")
    try:
        # 1. Keep it in memory so it doesn't unload automatically
        requests.post(OLLAMA_GENERATE_URL, json={"model": MODEL_NAME, "keep_alive": "1h"})
        
        # 2. Fire a tiny dummy request to fully initialize the context/KV cache
        client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Warming up context window."}],
            max_tokens=1
        )
        print("--- LLM WARMUP COMPLETE ---")
    except Exception as e:
        print(f"Warning: Could not warm up LLM: {e}")

def unload_model():
    """Forces Ollama to unload the model from memory to free resources."""
    print("--- UNLOADING LLM MODEL ---")
    try:
        # A keep_alive of 0 immediately frees the RAM/VRAM
        requests.post(OLLAMA_GENERATE_URL, json={"model": MODEL_NAME, "keep_alive": 0})
    except Exception as e:
        print(f"Warning: Could not unload LLM: {e}")

# knowledge base
def get_pdf_content():
    """Reads all text from any PDF files in the knowledge_vault folder."""
    pdf_text = ""
    vault_path = "knowledge_vault"
    
    if not os.path.exists(vault_path):
        return ""

    for filename in os.listdir(vault_path):
        if filename.endswith(".pdf"):
            try:
                with open(os.path.join(vault_path, filename), "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content = page.extract_text()
                        if content:
                            pdf_text += content + "\n"
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
    return pdf_text

def get_relevant_knowledge(user_input):
    text = user_input.lower()
    combined_info = ""
    
    # Load the JSON
    json_path = os.path.join("knowledge_vault", "knowledge.json")
    try:
        with open(json_path, "r") as file:
            knowledge_base = json.load(file)
    except FileNotFoundError:
        return "No specific lab knowledge found."

    # Check for keyword matches in the JSON and combine relevant info
    found_keywords = []
    for category_name, package_data in knowledge_base.items():
        if category_name == "default":
            continue
        for keyword in package_data["keywords"]:
            if keyword in text:
                found_keywords.append(category_name)
                combined_info += f"FACT ({category_name}): {package_data['info']}\n"
    
    if found_keywords:
        #print(f"Combined JSON matches: {', '.join(found_keywords)}")
            
    # Add default info at the end
        default_info = knowledge_base.get("default", {}).get("info", "")
        combined_info = f"GENERAL LAB RULES: {default_info}\n\n" + combined_info
    
    # Add PDF content
    pdf_info = get_pdf_content()
    if pdf_info:
        combined_info += f"\nTECHNICAL MANUAL DETAILS:\n{pdf_info[:2000]}" 
        
    return combined_info
        
# persona loading
def load_persona(filename=PERSONA_PATH):
    path = os.path.join("server/personas", filename)
    if not os.path.exists(path):
        return "You are a helpful assistant."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
# main response logic
def get_edi_response(user_input):
    global chat_history 
    
    current_package = get_relevant_knowledge(user_input)
    base_instructions = load_persona(PERSONA_PATH)
    
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
            model=MODEL_NAME, 
            messages=messages_to_send
        )
        
        response_text = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": response_text})
        
        print(completion)
        return response_text
        
    except Exception as e:
        if chat_history and chat_history[-1]["role"] == "user":
            chat_history.pop()

        return f"[SORRY] | Brain Error: {str(e)}"
    
def reset_memory():
    """Wipes EDI's short-term memory clean for the next session."""
    global chat_history
    chat_history = []
    print("API Triggered: EDI's memory has been completely wiped.")
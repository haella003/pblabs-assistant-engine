import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
from handler import knowledge_handler

load_dotenv() 

# Ensure this matches the model used in get_edi_response
MODEL_NAME = "gemma3:4b"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"

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
    """Reads ALL text from any PDF files in the server/knowledge_vault folder."""
    pdf_text = ""
    # FIXED: Point to the correct folder location
    vault_path = os.path.join("server", "knowledge_vault")
    
    if not os.path.exists(vault_path):
        print(f"Warning: Vault path not found at {vault_path}")
        return ""

    for filename in os.listdir(vault_path):
        if filename.endswith(".pdf"):
            print(f"Reading file from Knowledge Vault: {filename}")
            try:
                with open(os.path.join(vault_path, filename), "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page_num, page in enumerate(reader.pages):
                        content = page.extract_text()
                        if content:
                            pdf_text += content + "\n"
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
    return pdf_text

def get_relevant_knowledge(user_input):
    text = user_input.lower()
    combined_info = ""
    
    # 1. Load the JSON for hardcoded keyword rules
    json_path = os.path.join("server", "knowledge_vault", "knowledge.json")
    try:
        with open(json_path, "r") as file:
            knowledge_base = json.load(file)
    except FileNotFoundError:
        knowledge_base = {}

    for category_name, package_data in knowledge_base.items():
        if category_name == "default":
            continue
        for keyword in package_data.get("keywords", []):
            if keyword in text:
                combined_info += f"FACT ({category_name}): {package_data['info']}\n"
            
    # Add default lab info
    default_info = knowledge_base.get("default", {}).get("info", "")
    combined_info = f"GENERAL LAB RULES: {default_info}\n\n" + combined_info
    
    # 2. THE FAISS FIX: Ask the vector store to scan all 54 pages 
    # and return the top 4 most contextually relevant chunks matching the user's input!
    try:
        print(f"FAISS: Scanning 54-page index for matching context...")
        # k=4 pulls the 4 best matching paragraphs from anywhere in your document
        pdf_context = knowledge_handler.get_relevant_context(user_input, k=4)
        if pdf_context:
            combined_info += f"\nRETRIEVED THESIS & MANUAL CONTEXT:\n{pdf_context}"
    except Exception as e:
        print(f"Error retrieving context from FAISS: {e}")
        
    return combined_info
        
# main response logic
def get_edi_response(user_input):
    global chat_history 
    
    # 1. Fetch data from knowledge base
    current_package = get_relevant_knowledge(user_input)
    
    # 2. Dynamically load all text files in the personas folder
    personas_dir = "server/personas"
    persona_content = ""
    system_rules = ""
    prompt_blueprint = ""
    
    try:
        for filename in os.listdir(personas_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(personas_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Automatically sort content based on what the file is named
                if filename == "prompt_template.txt":
                    prompt_blueprint = content
                elif filename == "system_rules.txt":
                    system_rules = content
                else:
                    # Treat ANY other text file you drop in here as a persona!
                    persona_content += f"\n{content}"
    except Exception as e:
        print(f"Error loading prompt files dynamically: {e}")

    # 3. Stitch everything into the blueprint placeholders
    if prompt_blueprint:
        system_prompt = (
            prompt_blueprint
            .replace("{{persona}}", persona_content.strip())
            .replace("{{system_rules}}", system_rules)
            .replace("{{retrieved_context}}", current_package)
        )
    else:
        # Fallback if prompt_template.txt is missing or renamed
        system_prompt = f"{persona_content}\n\nSYSTEM RULES:\n{system_rules}\n\nCONTEXT:\n{current_package}"
    
    # 4. Append history and send to LLM
    chat_history.append({"role": "user", "content": user_input})
    
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
        
    messages_to_send = [{"role": "system", "content": system_prompt}] + chat_history
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=messages_to_send
        )
        
        # --- BULLETPROOF TEXT EXTRACTION ---
        try:
            # 1. Try standard OpenAI Object attribute access
            response_text = completion.choices[0].message.content
        except (AttributeError, TypeError):
            try:
                # 2. Try dict-style access if it was parsed as a pure dictionary
                response_text = completion.choices["message"]["content"]
            except Exception:
                # 3. Last resort: Convert the choice object to a string/dict structure
                # This handles complex legacy API edge cases
                choice_data = dict(completion.choices)
                if "message" in choice_data:
                    msg = choice_data["message"]
                    response_text = msg.get("content") if hasattr(msg, "get") else msg.content
                else:
                    raise Exception("Could not parse completion object payload structure.")
        # -------------------------------------
        
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
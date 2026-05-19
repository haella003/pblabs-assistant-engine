# Personas
This directory stores the core character profiles and personality definitions for EDI (EDucatIon). These text files act as specialized system prompts that dictate exactly how the local Large Language Model (Gemma 3) behaves, how it speaks, and what knowledge constraints it must follow.

## Directory Contents
* **`personas/EDI_bachelorthesis.txt` (Who you are):** Defines EDI's core character, background, informal tone, and unique style as a physical, orange-feathered lab entity.
* **`prompt_templates/system_rules.txt` (How you must behave):** Sets strict technical boundaries, safety guardrails, context constraints, and formatting rules. It tells EDI how to handle missing information and how to apply emotion tags.
* **`prompt_templates/prompt_template.txt` (The blueprint):** The structural layout file that stitches everything together. It dynamically combines the Persona, the System Rules, and the context retrieved from the FAISS database into a single cohesive prompt for the local LLM.

## Current Modes
### How Personas Work in the Pipeline
When the server initializes or handles a user request, the `llm_handler.py` reads these files and injects them directly into the LLM's context window. This ensures that EDI never breaks character and always frames information through its identity.

Every persona file enforces three main rules:

1. **Character Consistency:** Defines EDI's conversational tone (friendly and according to its attributes).
2. **Behavioral Constraints:** Prevents the AI from hallucinating or making up rules about lab equipment. If EDI doesn't find an answer in the retrieved FAISS documentation, the persona instructs it to honestly admit it doesn't know and suggest asking a human supervisor.
3. **Emotion & State Tagging:** Instructs the model to append emotional metadata tags (like `[happy]`, `[bored]`, `[thoughtful]` or `[curious]`) to its raw text replies. The server passes these tags to the client so that the frontend can trigger matching spatial animations.

### Creating or Editing a Persona
Because the system is fully modular, **swapping a character or adapting EDI for a new laboratory context is incredibly easy**. 
Since the technical guardrails and response formats are isolated in the `prompt_templates/` directory, you can completely change EDI’s entire identity, tone, and room context by simply uploading different text files in this `personas/` folder. The underlying AI engine, database connection, and voice processing loops remain entirely unchanged.

If you want to tweak how EDI talks or add a new persona, follow these guidelines inside the text files:
* Use clear, direct, first-person instructions (e.g. *"You are EDI, a helpful lab assistant. You speak casually but not rude."*).
* Define the formatting rules for response length so EDI's spoken answers (e.g. *"Make short answers, don't rephrase the question of the user, etc."*).


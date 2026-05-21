# Tests
## Directory Contents
This directory contains standalone diagnostic scripts used to test, isolate, and verify the individual modules of EDI's backend AI pipeline. 
Before integrating new features into the main frontend client application, use these scripts to ensure the local Large Language Model (LLM), speech generation loops, and custom character behaviors are functioning properly.

## Current Modes
Make sure your virtual environment is active (`source venv/bin/activate`) and your local server or Ollama engine is running before executing these tests. Run all scripts from the root directory of the repository.

### 1. Test the Text-to-Speech (TTS) Engine
* **File:** `test_voice.py`
* **Purpose:** Verifies that the local Piper TTS model can successfully access the `.onnx` files, parse text, and synthesize vocal audio outputs locally without errors.
* **How to run:**
  ```bash
  python3 server/testing/test_voice.py
  ```

### 2. Test Character Personas & Emotion Modes
* **File:** `test_edi_modes.py`
* **Purpose:** Tests the llm_handler.py and prompt structures. It simulates text queries to ensure that Gemma 3 correctly assumes EDI's personality, stays within the laboratory safety constraints, and appends the appropriate emotional tags (e.g., [happy], [thinking]) to its replies.
* * **How to run:**
  ```bash
  python3 server/tests/test_edi_modes.py
  ```

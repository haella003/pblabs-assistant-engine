# Server
This directory houses the core backend intelligence engine for EDI. Built with **FastAPI**, this server acts as the central hub; orchestrating all local AI tasks, handling session states, and providing the endpoints that the Mixed Reality headset client talks to.

## Directory Contents
* **`./handler`**: The functional AI modules (Whisper for STT, Piper for TTS, FAISS for RAG, and Ollama for the Gemma 3 LLM).
* **`./personas`**: Character system prompts (`EDI_bachelorthesis.txt`, `EDI_RZ_1.txt`) that give EDI its distinct personality and room knowledge.
* **`./piper_voices`**: Storage for local `.onnx` voice profiles used to quickly generate speech audio.
* **`./prompt_templates`**: Formatting rules, system constraints, and emotion tag guidelines for the LLM.
* **`./testing`**: Includes to test scripts (`test_edi_modes.py`, `test_voice.py`) to verify speech and conversational modes offline.
* **`main.py`**: The main entry point. It boots up the FastAPI application and tracks lifecycle states.

## Current Modes
The server functions as a deterministic state machine to ensure the client application knows exactly what EDI is doing at any given microsecond. 

The server transitions through these operational states during a standard user interaction loop:

```text
       ┌───────────┐
       │   IDLE    │ <───────────────────────────┐
       └─────┬─────┘                             │
             │ (User starts speaking)            │
             ▼                                   │
       ┌-───────────┐                            │
       │TRANSCRIBING│ (Whisper processes audio)  │
       └─────┬─────-┘                            │
             │                                   │
             ▼                                   │
       ┌───────────┐                             │
       │ THINKING  │ (FAISS fetches context      │
       └─────┬─────┘  + Gemma 3 generates reply) │
             │                                   │
             ▼                                   │
       ┌───────────┐                             │
       │ SPEAKING  │ (Piper plays/streams audio) │
       └─────┬─────┘                             │
             └───────────────────────────────────┘
```

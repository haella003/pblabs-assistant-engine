# Local LLM Assistant Engine

## Project Overview

### About
This project develops a mixed reality setup for PBLabs room instructions. PBLabs is a bookable ETH space for group workshops and meetings. Currently,
a lab staff member personally explains rules and equipment. The new solution uses Spatial Computing headset (Meta Quest 3) to provide an interactive introduction by a digital version of a Lab instructor called M. Next to M there will be an additional creature called EDI which should make the user experience (UX) more interactive. During this onboarding, users can freely talk with EDI, ask questions about the space, and receive tailored guidance on rules and equipment usage. A Python-based backend with a local large language model (LLM) processes their speech and generates replies, enabling natural, real-time question-answering in the mixed reality (MR) environment.

This repository contains the core intelligence engine. Built as a Semester Project the system introduces **EDI (EDucatIon)** - an interactive lab assistant. The backend architecture uses a FastAPI framework to orchestrate a fully localized AI stack, combining automated Speech-to-Text (SST) with Whisper, Retrieval-Augmented Generation with FAISS and Gemma 3, and fast local Text-to-Speech (TTS) synthesis with Piper. 

### The Reason for the Project
This project introduces a new approach for conveying educational, operational, and research content within an academic environment. By developing an adaptive, spatial tutoring prototype, it demonstrates how future university laboratories can scale their teaching and infrastructure. Traditionally, onboarding students and researchers require time and manual coordination from lab supervisors. Instead of relying on written manuals or a generic chatbot, this project brings static research data to life by injecting it directly into a **Mixed Reality (MR) spatial environment with a strong emphasis on personality-driven interaction**. 

The project implements three primary pillars:

1. **Context-Aware Retrieval-Augmented Generation (RAG):** EDI doesn't just chat; it uses semantic search to "read" the physical lab's documentation and precise thesis data, answering questions more accurate.
2. **First-Person Spatial Persona:** EDI is designed as a playful, digital entity materialized as a distinct physical structure (orange to match the room's interior). By processing dynamic emotion tags alongside the prompt, the backend allows EDI to react and state with conversational feedback.
4. **Fully Local & Private Stack:** To ensure complete data privacy and low-latency interaction inside the lab, the entire pipeline runs locally on a single machine without relying on external cloud APIs.

### Future Work
This repository is a first version and forms the basic technical framework. While this core engine already handles the basic local AI logic and voice interactions, there is still a lot that can be improved. Moving forward, the goal is to expand this prototype into a reliable, permanent setup that runs seamlessly inside the Media & Methods Lab (MML). 

1. **Advanced Interaction Mechanics & Session Lifecycle**
* **Dynamic Voice Activity Detection (VAD):** Implementing an audio gating logic to ensure EDI only speaks when the user is finished talking, immediately silences itself if interrupted by the user, and smoothly returns to an active listening state.
* **Session Lifecycle Boundaries:** Developing and testing definitive session termination logic (e.g., explicit "Goodbye" intent detection or timeout parameters) to clear conversational buffers, reset state flags, and prepare the engine for the next user.

2. **Multi-Deployment Modalities**
* **Standalone Desktop/Mobile Chat Application:** Packaging the backend pipeline alongside a lightweight frontend UI as a downloadable application, allowing students to text-chat with EDI's knowledge base outside of the physical lab room context.
* **Headset-Specific Conversational Tweaks:** Branching the backend orchestrator to support tailored system prompts and a bigger variety of emotional tag triggers.

3. **Unified Spatial Integration & Final Synthesis**
* **The Full Spatial Ecosystem:** The ultimate milestone is the seamless fusion of all development layers—unifying this Python backend engine with the Unreal Engine frontend client to synchronize live state events (`idle`, `transcribing`, `thinking`) directly with real-time spatial animations, particle effects, and character model triggers.
* **Unified Setup Installer:** Replacing manual command-line dependency setups with a compiled, single-click installer or Dockerized architecture to automate the configuration of local Ollama, Whisper, and Piper paths, lowering the barrier to entry for other research labs.

---
## Directory Structure

```text
pblabs-mr-onboarding-core/
├── .github/
│   └── ci.yml                      # Automated GitHub Actions Continuous Integration pipeline
├── client/
│   └── api_test_client.py          # Script to verify raw FastAPI endpoint behaviors and JSON responses
├── server/
│   ├── handler/
│   │   ├── audio_handler.py        # Speech-to-Text handler (Whisper)
│   │   ├── knowledge_handler.py    # Vector database search layer (FAISS)
│   │   ├── llm_handler.py          # Local LLM integration layer (Ollama)
│   │   ├── logger_handler.py       # Centralized system logging
│   │   └── speech_handler.py       # Text-to-Speech engine (Piper TTS)
│   ├── knowledge_vault/            # Source documents, PDFs, and FAISS indices
│   ├── personas/
│   │   ├── EDI_profile.txt         # Core personality profile definition
│   │   ├── prompt_template.txt     # System structural composition framework
│   │   └── system_rules.txt        # Behavioral constraints and emotion tag logic
│   ├── piper_voices/               # Local voice model storage files (.onnx / .onnx.json) for TTS
│   ├── tests/
│   │   ├── test_backend.py         # Automated structural unit test suite (executed by cloud CI)
│   │   ├── test_edi_modes.py       # Client CLI logic simulator for text/voice testing
│   │   └── test_voice.py           # Isolated test script specifically for checking the audio/voice pipeline
│   └── main.py                     # Primary FastAPI entry point and lifecycle state engine
├── .gitignore                      # Rules for excluding system artifacts from Git
├── LICENSE                         # MIT License documentation
├── README.md                       # Repository overview documentation
├── requirements.txt                # System Python dependencies
└── setup.sh                        # environment setup and dependency installer
```
Each subdirectory contains its own `README.md` file detailing localized installation notes, scripts, and configuration guidelines.

| Directory Path | Content Description |
| :--- | :--- |
| **`./client`** | Houses the frontend code, user interfaces, or Unity/MR headset application scripts that interact with the core backend service. |
| **`./server`** | The central FastAPI web server wrapper responsible for managing session states, lifecycle endpoints, and request routing. |
| **`./server/personas`** | Storage for identity profiles, containing `.txt` files that define behavioral guidelines and spatial context. |
| **`./server/piper_voices`** | Holds the local `.onnx` voice models and metadata configurations used by the text-to-speech synthesis engine for rapid audio generation. |
| **`./server/tests`** | Diagnostic scripts to verify speech and conversational modes offline. |

---
## Installation Guide
Follow these steps to set up your local development environment and get the Backend running.

### Prerequisites
Install these three things before running the code:
* **Python 3.9+**: Your local environment is verified on Python 3.9
* **Ollama**: For running local LLMs. [Download here](https://ollama.com/) 
* **Git**: Required to clone the repository code from GitHub and manage version control changes easily
  
### Setup Instructions
#### 0. Clone the Repository
```bash
git clone https://github.com/haella003/pblabs-assistant-engine.git
cd pblabs-assistant-engine
```

#### 1. Environment Setup
```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

#### 2. Start the Dependency Model Management
```bash
ollama pull gemma4:e4b
```

#### 3. Adjustments
The system is designed to be modular. Before running, adjust settings, network profiles, and AI behaviors by modifying specific configuration surfaces:
##### 3.1 Network Settings & IP Addresses
   By default, the server runs on your local machine (127.0.0.1:8080).
   If you are connecting an external device (like a standalone VR/MR headset or a separate Unreal Engine machine over a local Wi-Fi network), you must bind the server to your computer's local      IP address:
   - Open `server/main.py`.
   - Scroll to the very bottom file execution line: uvicorn.run(app, host="127.0.0.1", port=8080).
   - Change "127.0.0.1" to your local network IP or use "0.0.0.0" to listen on all active network interfaces.
##### 3.2 Accessing Local API
   Use this if you want to manually trigger the LLM, Whisper, and Piper TTS endpoints directly from your browser.:
   - **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8080/docs)
##### 3.3 Swapping Persona Files
   It is possible to change the complete background identity or role-play parameters without altering code:
   - Navigate to the `server/personas/` directory and adjust if wanted
   - Modify the content inside `server/knowledge_vault`, or drop in a completely new `.txt` or `.pdf` profile. The backend automatically parses any extra text file.
##### 3.4 Model Tuning & Optimization
   To improve response quality and ensure the AI can handle long-form conversations (high memory), you can adjust the context length manually under: Ollama > Settings > Context Length.

#### 4. Running the System
##### 4.1 Start the FastAPI Server
```bash
python3 server/main.py
```

##### 4.2 Verify and Test the System
To ensure everything is working before connecting the Unreal Engine frontend, keep your server running in Terminal Window 1. Open a new Terminal Window 2, navigate to the project directory, activate the environment `source venv/bin/activate`, and run the local testing suite:
```bash
python3 server/tests/test_edi_modes.py
```

#### 5. Setup Unreal Engine
XXX

---
## Contributors

This Semester project was developed at ETH Zurich in cooperation with the [Global Health Engineering Lab (GHE)](https://ghe.ethz.ch/) and the [Media & Methods Lab (MML)](https://www.mediamethodslab.ethz.ch/).

* Ella Haechler: Author & Maintainer
* Elizabeth Tilley: Supervisor
* Jakub Tkaczuk: Supervisor
* Jeanine Reutemann: Supervisor
* Daniel Borges: Supervisor & Technical Support

## License

This Project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Thesis Context
Date: Spring Semester 2026

Location: Zürich, Switzerland

Institution: ETH Zurich, Switzerland

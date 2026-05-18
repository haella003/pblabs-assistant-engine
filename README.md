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

## Directory Structure

```text
pblabs-mr-onboarding-core/
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
│   │   ├── EDI_bachelorthesis.txt  # Core personality profile definition
│   │   ├── prompt_template.txt     # System structural composition framework
│   │   └── system_rules.txt        # Behavioral constraints and emotion tag logic
│   ├── piper_voices/               # Local voice model storage files (.onnx / .onnx.json) for TTS
│   ├── testing/
│   │   ├── test_edi_modes.py       # Client CLI logic simulator for text/voice testing
│   │   └── test_voice.py           # Isolated test script specifically for checking the audio/voice pipeline
│   └── main.py                     # Primary FastAPI entry point and lifecycle state engine
├── venv/                           # Isolated local Python virtual environment
├── LICENSE                         # MIT License documentation
├── requirements.txt                # System Python dependencies
└── README.md                       # Repository overview documentation
```
Each subdirectory contains its own `README.md` file detailing localized installation notes, scripts, and configuration guidelines.

| Directory Path | Content Description |
| :--- | :--- |
| **`./client`** | Houses the frontend code, user interfaces, or Unity/MR headset application scripts that interact with the core backend service. |
| **`./server`** | The central FastAPI web server wrapper responsible for managing session states, lifecycle endpoints, and request routing. |
| **`./server/handler`** | Contains the core modular AI engines, including handlers for local Whisper (STT), Piper (TTS), FAISS vector search, and Ollama (LLM orchestration). |
| **`./server/personas`** | Storage for identity profiles, containing `.txt` files that define behavioral guidelines and spatial context. |
| **`./server/piper_voices`** | Holds the local `.onnx` voice models and metadata configurations used by the text-to-speech synthesis engine for rapid audio generation. |

## Installation Guide

### 0. Prerequisites
Install these three things before running the code:
1. **Ollama**: [Download here](https://ollama.com/). 
   - After installing, you **must** download the specific model used in this project by running this command in your terminal:
   ```bash
   ollama pull gemma3:4b
2. **FFmpeg**: 
   - Mac: `brew install ffmpeg`
   - Windows: `choco install ffmpeg`
3. **Python 3.10+**
   In your python code, it should look like this:
   response = ollama.chat(model='gemma4:4b', messages=[...])

### 1. Setup Instructions

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install universal libraries
pip install -r requirements.txt
```

### 2. Voice Models

Download en_US-amy-medium.onnx and en_US-amy-medium.onnx.json from HuggingFace.

Save them in: server/piper_voices/

### 3. Configuration & Adjustments

Before running the project, check these three items:

#### a. Network Settings (for VR Users)
If you are running the backend on a PC and the client on a separate VR headset:
- Open `server/api_main.py`.
- Change the host from `127.0.0.1` to your PC's actual IP address (e.g., `192.168.1.XX`).

#### b. Character Persona
To change EDI's personality or knowledge base:
- Navigate to the `server/personas/` folder.
- Adjust the `.json` or `.txt` persona file to match your project's requirements.

#### c. Requirements
Ensure all libraries are installed correctly for your specific OS:
```bash
pip install -r requirements.txt
```

### 5. How To Run
Start the Backend:

```bash
python server/api_main.py
```
Start the Interface:

```bash
python start_edi.py
```

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

Institution: ETH Zurich (Eidgenössische Technische Hochschule Zürich)

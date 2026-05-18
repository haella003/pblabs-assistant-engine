# Local LLM Assistant Engine


## Project Overview
XYZ

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

- Ella Haechler: Author & Maintainer
- Elizabeth Tilley: Supervisor
- Jakub Tkaczuk: Supervisor
- Jeanine Reutemann: Supervisor
- Daniel Borges: Supervisor & Technical Support

## License

This Project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Thesis Context
Date: Spring Semester 2026

Location: Zürich, Switzerland

Institution: ETH Zurich (Eidgenössische Technische Hochschule Zürich)

# EDI INSTALLTION KIT

## 0. Prerequisites
Install these three things before running the code:
1. **Ollama**: [Download here](https://ollama.com/). 
   - After installing, you **must** download the specific model used in this project by running this command in your terminal:
   ```bash
   ollama pull gemma:4b
2. **FFmpeg**: 
   - Mac: `brew install ffmpeg`
   - Windows: `choco install ffmpeg`
3. **Python 3.10+**
   # In your python code, it should look like this:
   response = ollama.chat(model='gemma4:4b', messages=[...])

---

## 1. Setup Instructions

### Environment & Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install universal libraries
pip install -r requirements.txt
```
---

### 2. Voice Models

Download en_US-amy-medium.onnx and en_US-amy-medium.onnx.json from HuggingFace.

Save them in: server/piper_voices/

---

## 3. Configuration & Adjustments

Before running the project, check these three items:

### a. Network Settings (for VR Users)
If you are running the backend on a PC and the client on a separate VR headset:
- Open `server/api_main.py`.
- Change the host from `127.0.0.1` to your PC's actual IP address (e.g., `192.168.1.XX`).

### b. Character Persona
To change EDI's personality or knowledge base:
- Navigate to the `server/personas/` folder.
- Adjust the `.json` or `.txt` persona file to match your project's requirements.

### c. Requirements
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


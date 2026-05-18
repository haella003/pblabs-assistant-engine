# Piper Voices
This directory holds the localized audio assets and model files used by the Text-to-Speech (TTS) engine, **Piper**. Piper relies on these local files to instantly synthesize text replies into speech without the need of an internet connection.

## Directory Contents
For every voice profile used by the system, this folder contains a matching pair of files:

1. **`.onnx` File (The Model weights):** The compiled neural network file that contains the actual voice data.
2. **`.onnx.json` File (The Config file):** The metadata configuration file. It tells Piper how to parse the text, how to handle phonemes (pronunciations), and contains the sample rate variables for the speaker.

## Current Modes
Piper supports a massive library of open-source voices across different qualities (`low`, `medium`, `high`). If you want to change EDI's voice profile:

1. Download the preferred voice pair (`.onnx` and `.onnx.json`) from the official [Piper Voice Repository](https://github.com/OHF-Voice/piper1-gpl) according to your operating system.
2. Drop both files directly into this directory.
3. Update the directory path and model file strings inside your `speech_handler.py` (or your central server configuration) to point to the new filenames.

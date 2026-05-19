# Client
This directory is designated for the frontend user interface and Mixed Reality (MR) application scripts that interact with the backend engine.

## Directory Contents
* **`api_test_client.py`**: A python script used to test and verify the raw connection between the client side and the FastAPI backend server endpoints. It simulates basic network requests to ensure everything communicates properly before launching full headset apps.

## Current Modes
Right now, the project is structured to separate the client (the headset/visual layer) from the server (the AI pipeline brain). 

* **State Tracking:** The client is designed to send audio or text requests to the server and listen for state updates (`idle`, `transcribing`, `thinking`) to drive the user experience.
* **Core Connection:** All client applications interact with the central backend via REST API endpoints hosted locally at `http://127.0.0.1:8080`.

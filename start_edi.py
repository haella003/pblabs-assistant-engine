import multiprocessing
import uvicorn
import main_api
from main_api import app
import main
import state

def run_api(shared_data):
    main_api.shared_state = shared_data
    uvicorn.run(app, host="127.0.0.1", port=8080)

def run_brain(shared_data):
    main.run_edi_loop(shared_data)

if __name__ == "__main__":
    # This creates the shared memory
    manager = multiprocessing.Manager()
    shared_data = manager.dict(state.shared_state)

    p1 = multiprocessing.Process(target=run_api, args=(shared_data,))
    p2 = multiprocessing.Process(target=run_brain, args=(shared_data,))

    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
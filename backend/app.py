from fastapi import FastAPI
from data_processing import get_info
from eeg_controller import start_eeg_stream, process_eeg_data
from websocket import websocket_endpoint

app = FastAPI()
@app.get("/start_stream")
async def start_stream():
    serial_port = '/dev/ttyUSB0'
    board = await start_eeg_stream(serial_port)
    
    return {"status": "Stream started" }

app.websocket("/ws")(websocket_endpoint)

import asyncio
from fastapi import FastAPI, WebSocket
from data_processing import get_info
from eeg_controller import get_real_time_eeg_data, prepare_eeg_stream, process_eeg_data, start_streaming
from config import BOARD, SERIAL_PORT, AWS, AWS_TOKEN, AWS_ENDPOINT

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/prepare_stream")
async def prepare_stream():
    serial_port = SERIAL_PORT
    await prepare_eeg_stream(serial_port)
    return {"status": "Board prepared"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    await prepare_stream()
    global_board = await start_streaming()
    try:
        while True:
            data = await get_real_time_eeg_data()
            if data:
                await websocket.send_json((data))
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if global_board:
            global_board.stop_stream()
        await websocket.close()
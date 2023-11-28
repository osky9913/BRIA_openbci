import asyncio
from fastapi import WebSocket

from eeg_controller import get_real_time_eeg_data, process_eeg_data, start_eeg_stream


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    board = await start_eeg_stream('/dev/ttyUSB0')  # Start streaming when WebSocket connects
    try:
        while True:
            data = await get_real_time_eeg_data(board)
            if data:
                await websocket.send_json((data))
            await asyncio.sleep(0.5)  # Adjust timing as needed
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        board.stop_stream()
        board.release_session()
        await websocket.close()
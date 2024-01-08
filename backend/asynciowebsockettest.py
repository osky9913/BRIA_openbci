import asyncio
import websockets
import numpy as np

async def test_websocket():
    uri = "ws://127.0.0.1:8000/bci_features"  # Replace with your actual WebSocket URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = eval(await websocket.recv())
            print(type(data))
            f = open("demofile2.txt", "a")
            f.write(f"Received data: {np.array(data).shape}\n")
            f.close()

asyncio.get_event_loop().run_until_complete(test_websocket())
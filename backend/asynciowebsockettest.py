import asyncio
import websockets

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws"  # Replace with your actual WebSocket URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"Received data: {data}")

asyncio.get_event_loop().run_until_complete(test_websocket())
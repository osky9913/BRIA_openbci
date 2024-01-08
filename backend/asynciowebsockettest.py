import asyncio
import websockets
import numpy as np

async def test_websocket1():
    uri = "ws://127.0.0.1:8000/ws"  # Replace with your actual WebSocket URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = eval(await websocket.recv())
            print(type(data))
            f = open("demofile1.txt", "a")
            f.write(f"Received data: {np.array(data).shape}\n")
            f.close()

async def test_websocket2():
    uri = "ws://127.0.0.1:8000/ica"  # Replace with your actual WebSocket URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = eval(await websocket.recv())
            print(type(data))
            f = open("demofile2.txt", "a")
            f.write(f"Received data: {np.array(data).shape}\n")
            f.close()

async def test_websocket3():
    uri = "ws://127.0.0.1:8000/fft"  # Replace with your actual WebSocket URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = eval(await websocket.recv())
            print(type(data))
            f = open("demofile3.txt", "a")
            f.write(f"Received data: {np.array(data).shape}\n")
            f.close()



async def main():
    await asyncio.gather(
        test_websocket1(),
        test_websocket2(),
        test_websocket3()
    )

if __name__ == "__main__":
    asyncio.run(main())
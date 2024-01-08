import asyncio
from fastapi import FastAPI, WebSocket
from data_processing import  get_info, process_data_with_fft
from eeg_controller import get_real_time_eeg_data, prepare_eeg_stream, process_eeg_data, start_streaming
from config import BOARD, SERIAL_PORT, AWS, AWS_TOKEN, AWS_ENDPOINT
import boto3
import json 
from datetime import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np



app = FastAPI()
kinesis_client = None
global_board = None
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
    session = boto3.Session()
    global kinesis_client

    # Create a Kinesis client using the session
    kinesis_client = session.client('kinesis', region_name='eu-north-1')

    return {"status": "Board prepared"}

@app.get("/get_info")
async def send_info():
    return get_info()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global global_board
    await websocket.accept()
    #await prepare_stream()
    if global_board == None:
        global_board = await start_streaming()
    try:
        while True:
            data = await get_real_time_eeg_data(ica=False)
            if data:
                print("Sending")
                await websocket.send_json((data))
                stream_name = 'eeg-stream'  # Replace with your Kinesis stream name
                partition_key = str(datetime.utcnow())
                #send_to_kinesis(stream_name, partition_key, data)


            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"WebSocket error: {e}")
        
    finally:
        if global_board:
            global_board.stop_stream()
        await websocket.close()


@app.websocket("/ica")
async def websocket_ica_wendpint(websocket: WebSocket):
    global global_board
    await websocket.accept()
    #await prepare_stream()
    if global_board == None:
        global_board = await start_streaming()
    try:
        while True:
            data = await get_real_time_eeg_data(ica=True)
            if data:
                await websocket.send_json((data))
                print((data))
                stream_name = 'eeg-stream'  # Replace with your Kinesis stream name
                partition_key = str(datetime.utcnow())
                #send_to_kinesis(stream_name, partition_key, data)


            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"WebSocket error: {e}")
        
    finally:
        #if global_board:
            #global_board.stop_stream()
        await websocket.close()

@app.websocket("/fft")
async def fft_websocket_endpoint(websocket: WebSocket):
    print("I am here")
    global global_board
    await websocket.accept()
    if global_board == None:
        global_board = await start_streaming()

    try:
        while True:
            data = await get_real_time_eeg_data()
            print("I am here2")
            
            if data:
                print("I am her3e")
                
                fft_data = process_data_with_fft(data)

                await websocket.send_json((fft_data))

            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"WebSocket error: {e}")
        
    finally:
        if global_board:
            global_board.stop_stream()
        await websocket.close()



"""
@app.websocket("/bci_features")
async def bci_features_websocket_endpoint(websocket: WebSocket):
    global global_board
    await websocket.accept()
    if global_board == None:
        global_board = await start_streaming()

    try:
        while True:
            eeg_data = await get_real_time_eeg_data()
            if eeg_data:
                plot_5d_bci_features(eeg_data,125)
                exit(1)
                bci_features = extract_bci_features(eeg_data)
                await websocket.send_json(bci_features)
            
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if global_board:
            global_board.stop_stream()
        await websocket.close()
"""
        
def send_to_kinesis(stream_name, partition_key, data):
    global kinesis_client

    """
    Send data to an AWS Kinesis stream.

    :param stream_name: The name of the Kinesis stream
    :param partition_key: A partition key to distribute data across shards
    :param data: Data to send (must be a JSON-serializable object)
    """
    try:
        # Convert the data to JSON and encode it to bytes
        data_blob = json.dumps(data).encode()
        print("DATABLOB")
        print(data_blob)

        # Put the record into the Kinesis stream
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=data_blob,
            PartitionKey=partition_key
        )

        print("Record sent to Kinesis:", response)

    except Exception as e:
        print("Error sending record to Kinesis:", e)

# Example usage
 # Using current timestamp as partition key




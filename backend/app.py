import asyncio
from fastapi import FastAPI, WebSocket
from data_processing import get_info
from eeg_controller import get_real_time_eeg_data, prepare_eeg_stream, process_eeg_data, start_streaming
from config import BOARD, SERIAL_PORT, AWS, AWS_TOKEN, AWS_ENDPOINT
import boto3
import json 
from datetime import datetime


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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global global_board
    await websocket.accept()
    #await prepare_stream()
    if global_board == None:
        global_board = await start_streaming()
    try:
        while True:
            data = await get_real_time_eeg_data()
            if data:
                await websocket.send_json((data))
                stream_name = 'eeg-stream'  # Replace with your Kinesis stream name
                partition_key = str(datetime.utcnow())
                send_to_kinesis(stream_name, partition_key, data)


            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"WebSocket error: {e}")
        
    finally:
        if global_board:
            global_board.stop_stream()
        await websocket.close()





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


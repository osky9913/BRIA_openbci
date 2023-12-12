import boto3
import json
from datetime import datetime

# Initialize a session using boto3
session = boto3.Session()

# Create a Kinesis client using the session
kinesis_client = session.client('kinesis', region_name='eu-north-1')

def send_to_kinesis(stream_name, partition_key, data):
    """
    Send data to an AWS Kinesis stream.

    :param stream_name: The name of the Kinesis stream
    :param partition_key: A partition key to distribute data across shards
    :param data: Data to send (must be a JSON-serializable object)
    """
    try:
        # Convert the data to JSON and encode it to bytes
        data_blob = json.dumps(data).encode()

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
stream_name = 'eeg-stream'  # Replace with your Kinesis stream name
partition_key = str(datetime.utcnow())  # Using current timestamp as partition key
dummy_data = {
    'sensor_id': 123,
    'value': 456,
    'timestamp': str(datetime.utcnow())
}

send_to_kinesis(stream_name, partition_key, dummy_data)

import psycopg2
import base64
import json



def lambda_handler(event,context):

    print("Recevied event:", event)
    
    conn = psycop2.connect(
        host="",
        dbmane="sampleDB",
        user="postgres",
        password="postgres1234567890",
        port="5432"
    )

    cursor = conn.cursor()


    print("Connected to the db")
    return {
        'statusCode': 200,
        'body': 'Success'
    }


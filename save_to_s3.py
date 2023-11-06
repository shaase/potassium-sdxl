import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv() 

def save_to_s3(payload):
    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = 'model-payloads'
    folder_name = 'outputs'

    # Initialize the S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Construct the destination key within the bucket
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]
    destination_key = os.path.join(folder_name, "output_" + timestamp + ".png")

    # Upload the payload to the specified S3 location
    s3.put_object(Body=payload, Bucket=bucket_name, Key=destination_key)

    output_path = bucket_name + "/" + destination_key
    return output_path
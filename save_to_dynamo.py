import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv() 

def save_to_dynamo(Item):
    # Set your AWS credentials as environment variables
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    TableName = 'TableName'

    # Initialize the DynamoDB client
    dynamodb = boto3.client('dynamodb')

    # Save the data to DynamoDB
    # item = dynamodb.put_item(TableName=TableName, Item={'fruitName':{'S':'Banana'},'key2':{'N':'value2'}})
    dItem = dynamodb.put_item(TableName=TableName, Item=Item)

    return dItem
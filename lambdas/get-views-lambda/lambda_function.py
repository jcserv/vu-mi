import boto3
import json
import os
from aws_lambda_typing import context as context_
from boto3.dynamodb.conditions import Key
from typing import Dict

REGION = os.environ.get("AWS_REGION")
QUEUE_URL = os.environ.get("QUEUE_URL")
VIEW_COUNTS_TABLE_NAME = os.environ.get("VIEW_COUNTS_TABLE_NAME")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(VIEW_COUNTS_TABLE_NAME)

sqs = boto3.client("sqs", region_name=REGION)


def lambda_handler(event: Dict, context: context_.Context):
    user_id = event["queryStringParameters"]["id"]
    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(user_id),
            Limit=250,
            ConsistentRead=True,
        )
        items = response.get("Items", [])

        view_count = 0
        if len(items) > 0:
            user_data = items[0]
            view_count = user_data.get("count", 0) + len(items) - 1

        send_message_sqs(user_id, view_count)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "schemaVersion": 1,
                    "label": "views",
                    "message": str(view_count),
                    "color": "blue",
                }
            ),
        }
    except Exception as e:
        print(f"An exception occurred when handling an event: {str(e)}")
        return {"statusCode": 500, "body": json.dumps("Internal server error")}


def send_message_sqs(user_id: str, count: int):
    try:
        message = {
            "userId": user_id,
            "count": count,
        }

        response = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=str(message))
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")

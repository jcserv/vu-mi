import boto3
import json
import re
import os
from aws_lambda_typing import context as context_, events
from datetime import datetime, timedelta, timezone

REGION=os.environ.get("AWS_REGION")
VIEW_COUNTS_TABLE_NAME=os.environ.get("VIEW_COUNTS_TABLE_NAME")

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(VIEW_COUNTS_TABLE_NAME)

def lambda_handler(event: events.SQSEvent, context: context_.Context) -> None:
    for message in event["Records"]:
        process_message(convert_str_to_json(message["body"]))

def process_message(body: dict):
    user_id = body.get('userId', '')
    count = body.get('count', 0)
    try:
        if count == 0:
            initialize_user(user_id)
        put_view(user_id)

    except Exception as err:
        print(f"Unable to process message for user {user_id}: {err}")

def initialize_user(user_id):
    try:
        item = {
            "PK": user_id,
            "SK": "USER",
            "count": 0
        }
        response = table.put_item(
            Item=item,
        )
    except Exception as e:
        print(f"Error initializing user {user_id}: {str(e)}")
        raise e

def put_view(user_id):
    curr_time = datetime.now(timezone.utc)
    five_minutes_in_seconds = (5 * 60) - (curr_time.minute % 5) * 60 - curr_time.second
    try:
        item = {
            "PK": user_id,
            "SK": f'VIEW#{curr_time.isoformat()}',
            "ttl": int((curr_time + timedelta(seconds=five_minutes_in_seconds)).timestamp()),
        }
        response = table.put_item(
            Item=item,
        )
    except Exception as e:
        print(f"Error putting view for {user_id}: {str(e)}")
        raise e

def convert_str_to_json(s: str) -> dict:
    s = s.replace("'", '"')
    s = re.sub(r'Decimal\("(\d+\.?\d*)"\)', r'\1', s)
    body = json.loads(s)
    return body
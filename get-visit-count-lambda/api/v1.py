import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict

router = APIRouter(prefix="/view-counts")

REGION=os.environ.get("AWS_REGION")
QUEUE_URL=os.environ.get("QUEUE_URL")
VIEW_COUNTS_TABLE_NAME=os.environ.get("VIEW_COUNTS_TABLE_NAME")

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(VIEW_COUNTS_TABLE_NAME)

sqs = boto3.client('sqs', region_name=REGION)

class ViewCountResponse(BaseModel):
    schemaVersion: int
    label: str
    message: str
    color: str

@router.get("/{user_id}", response_model=ViewCountResponse)
async def get_view_count(user_id: str) -> Dict[str, str]:
    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(user_id),
            Limit=250,
            ConsistentRead=True,
        )
        items = response.get('Items', [])

        view_count = 0
        if len(items) > 0:
            user_data = items[0]
            view_count = user_data.get('count', 0) + len(items) - 1

        send_message_sqs(user_id, view_count)

        return {
            "schemaVersion": 1,
            "label": "views",
            "message": str(view_count),
            "color": "blue"
        }
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def send_message_sqs(user_id: str, count: int):
    try:
        message = {
            'userId': user_id,
            'count': count,
        }
        
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=str(message)
        )    
    except Exception as e:
        print(f"Error sending message to SQS: {str(e)}")
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
from typing import Dict

router = APIRouter()

REGION=os.environ.get("AWS_REGION")
VIEW_COUNTS_TABLE_NAME=os.environ.get("VIEW_COUNTS_TABLE_NAME")

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(VIEW_COUNTS_TABLE_NAME)

class ViewCountResponse(BaseModel):
    schemaVersion: int
    label: str
    message: str
    color: str

@router.get("/{userId}", response_model=ViewCountResponse)
async def get_view_count(userId: str) -> Dict[str, str]:
    try:
        response = table.query(
            KeyConditionExpression=Key('PK').eq(userId)
        )
        items = response.get('Items', [])

        if not items:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = items[0]
        view_count = user_data.get('view_count', 0)

        return {
            "schemaVersion": 1,
            "label": "views",
            "message": str(view_count),
            "color": "blue"
        }
    except HTTPException as e:
        raise e  # Re-raise the HTTPException so it retains its status code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
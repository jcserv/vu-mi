import boto3
import json
import os
from aws_lambda_typing import context as context_, events

REGION=os.environ.get("AWS_REGION")
VIEW_COUNTS_TABLE_NAME=os.environ.get("VIEW_COUNTS_TABLE_NAME")

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(VIEW_COUNTS_TABLE_NAME)

def lambda_handler(event: events.DynamoDBStreamEvent, context: context_.Context):
    user_totals = {}
    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            item = record['dynamodb']
            user_id = item['Keys']['PK']['S']
            user_totals[user_id] = user_totals.get(user_id, 0) + 1

    for user_id, total in user_totals.items():
        try:
            response = table.get_item(Key={'PK': user_id})
            current_total = 0

            if 'Item' in response:
                current_total = response['Item'].get('totalCount', 0)            
            
            item = {
                'PK': user_id,
                'SK': "USER",
                'COUNT': current_total + total
            }

            table.put_item(
                Item=item,
            )
        except Exception as e:
            print(f"Error updating user view count for {user_id}: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
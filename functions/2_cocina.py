import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')

def lambda_handler(event, context):
    print(f"--- INICIO COCINA --- ID: {event.get('id')}")
    
    time.sleep(3)
    
    table.update_item(
        Key={'id': event['id']},
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':status': 'KITCHEN_READY'}
    )
    
    event['status'] = 'KITCHEN_READY'
    return event
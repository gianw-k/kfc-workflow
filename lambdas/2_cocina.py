import json
import boto3
import time
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'Orders'))

def lambda_handler(event, context):
    print(f"--- INICIO COCINA (MS Cocina) --- ID: {event.get('id')}")
    
    order_id = event['id']
    
    # Simular tiempo de cocción
    time.sleep(3)
    
    try:
        table.update_item(
            Key={'id': order_id},
            UpdateExpression="SET #s = :status, updatedAt = :now",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':status': 'KITCHEN_READY',
                ':now': datetime.now().isoformat()
            }
        )
        print(f"Orden {order_id} actualizada a KITCHEN_READY en DynamoDB")
    except Exception as e:
        print(f"Error actualizando DynamoDB: {str(e)}")
        raise
    
    event['status'] = 'KITCHEN_READY'
    return event
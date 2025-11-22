import json
import boto3
import time
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'Orders'))

def lambda_handler(event, context):
    print(f"--- INICIO EMPAQUE (MS Empaque) --- ID: {event.get('id')}")
    
    order_id = event['id']
    
    # Simular tiempo de empaque
    time.sleep(2)
    
    try:
        table.update_item(
            Key={'id': order_id},
            UpdateExpression="SET #s = :status, updatedAt = :now",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':status': 'PACKED',
                ':now': datetime.now().isoformat()
            }
        )
        print(f"Orden {order_id} actualizada a PACKED en DynamoDB")
    except Exception as e:
        print(f"Error DynamoDB: {str(e)}")
        raise
    
    event['status'] = 'PACKED'
    event['message'] = "Pedido empaquetado"
    return event
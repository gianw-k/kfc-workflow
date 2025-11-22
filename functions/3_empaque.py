import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')

def lambda_handler(event, context):
    print(f"--- INICIO EMPAQUE --- ID: {event.get('id')}")
    
    time.sleep(2)
    
    try:
        table.update_item(
            Key={'id': event['id']},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':status': 'PACKED'}
        )
    except Exception as e:
        print(f"Error DynamoDB: {str(e)}")
        # Continuamos para no romper el flujo en demo
    
    event['status'] = 'PACKED'
    event['message'] = "Pedido empaquetado"
    return event
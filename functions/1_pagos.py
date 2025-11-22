import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')

def lambda_handler(event, context):
    print(f"--- INICIO PAGOS --- ID: {event.get('id')}")
    
    # Validamos que llegue el ID
    if 'id' not in event:
        raise ValueError("Falta el ID del pedido")

    # 1. Simular validación de pago
    time.sleep(2)
    payment_id = "TXN-STRIPE-OK"
    
    # 2. Actualizar DynamoDB
    table.update_item(
        Key={'id': event['id']},
        UpdateExpression="SET #s = :status, paymentId = :pid",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':status': 'PAID', ':pid': payment_id}
    )
    
    # 3. Retornar datos
    event['status'] = 'PAID'
    event['paymentId'] = payment_id
    return event
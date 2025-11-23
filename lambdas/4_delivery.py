import json
import boto3
import random
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'Orders'))
event_bus = os.environ.get('EVENT_BUS', 'orders-bus')

def lambda_handler(event, context):
    print(f"--- INICIO DELIVERY (MS Delivery) --- ID: {event.get('id')}")
    
    order_id = event['id']
    
    # Asignar motorizado aleatorio
    drivers = ["Juan Perez", "Maria Lopez", "Carlos Ruiz", "Ana Diaz"]
    driver_asignado = random.choice(drivers)
    
    # 1. Actualizar DynamoDB con estado DELIVERING y driver asignado
    try:
        table.update_item(
            Key={'id': order_id},
            UpdateExpression="SET #s = :status, driver = :d, updatedAt = :now",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':status': 'DELIVERING',
                ':d': driver_asignado,
                ':now': datetime.now().isoformat()
            }
        )
        print(f"Orden {order_id} actualizada a DELIVERING en DynamoDB con driver {driver_asignado}")
    except Exception as e:
        print(f"Error actualizando DynamoDB: {str(e)}")
        raise
    
    # 2. Enviar evento ORDER.READY a EventBridge "Pedido Listo"
    try:
        events.put_events(
            Entries=[{
                'Source': 'kfc.orders',
                'DetailType': 'ORDER.READY',
                'EventBusName': event_bus,
                'Detail': json.dumps({
                    'orderId': order_id,
                    'status': 'DELIVERING',
                    'driver': driver_asignado
                })
            }]
        )
        print(f"Evento ORDER.READY enviado a EventBridge para orden {order_id}")
    except Exception as e:
        print(f"Advertencia: No se pudo enviar evento ORDER.READY a EventBridge: {str(e)}")
        # Continuamos porque el estado ya se actualizó

    event['status'] = 'DELIVERING'
    event['driver'] = driver_asignado
    return event
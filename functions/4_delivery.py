import json
import boto3
import random

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PedidosKFC')
events = boto3.client('events')

def lambda_handler(event, context):
    print(f"--- INICIO DELIVERY --- ID: {event.get('id')}")
    
    drivers = ["Juan Perez", "Maria Lopez", "Carlos Ruiz", "Ana Diaz"]
    driver_asignado = random.choice(drivers)
    
    table.update_item(
        Key={'id': event['id']},
        UpdateExpression="SET #s = :status, driver = :d",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':status': 'DELIVERING',
            ':d': driver_asignado
        }
    )
    
    # EventBridge (Protegido con try/except para Labs)
    try:
        events.put_events(
            Entries=[{
                'Source': 'kfc.workflow',
                'DetailType': 'PedidoEnCamino',
                'Detail': json.dumps({'id': event['id'], 'status': 'DELIVERING'}),
                'EventBusName': 'default'
            }]
        )
    except Exception as e:
        print(f"Nota: No se pudo enviar evento a EventBridge: {str(e)}")

    event['status'] = 'DELIVERING'
    event['driver'] = driver_asignado
    return event
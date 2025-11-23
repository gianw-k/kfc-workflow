import json
import boto3
import time
import os
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'Orders'))
event_bus = os.environ.get('EVENT_BUS', 'orders-bus')

def lambda_handler(event, context):
    print(f"--- INICIO PAGOS (MS Pagos) --- ID: {event.get('id')}")
    
    # Validamos que llegue el ID
    if 'id' not in event:
        raise ValueError("Falta el ID del pedido")

    order_id = event['id']
    
    # 1. Validar pago con Stripe (simulación)
    time.sleep(2)  # Simular latencia de Stripe
    
    # Simular rechazo de pago si el total es mayor a 500 o si el ID contiene "REJECTED"
    total = event.get('total', 0)
    if total > 500 or 'REJECTED' in order_id:
        print(f"Pago RECHAZADO para orden {order_id} (Total: {total})")
        # Actualizar estado a REJECTED
        try:
            table.update_item(
                Key={'id': order_id},
                UpdateExpression="SET #s = :status, updatedAt = :now",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':status': 'PAYMENT_REJECTED',
                    ':now': datetime.now().isoformat()
                },
                ConditionExpression='attribute_exists(id)'
            )
            print(f"Orden {order_id} actualizada a PAYMENT_REJECTED en DynamoDB")
        except Exception as e:
            print(f"Error actualizando DynamoDB: {str(e)}")
        
        # Retornar estado rechazado para que el workflow lo maneje
        event['status'] = 'PAYMENT_REJECTED'
        event['paymentId'] = None
        return event
    
    payment_id = f"PAY-STRIPE-{int(time.time())}"
    
    # 2. Actualizar DynamoDB con el estado PAID
    try:
        table.update_item(
            Key={'id': order_id},
            UpdateExpression="SET #s = :status, paymentId = :pid, updatedAt = :now",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':status': 'PAID',
                ':pid': payment_id,
                ':now': datetime.now().isoformat()
            },
            ConditionExpression='attribute_exists(id)'  # La orden debe existir
        )
        print(f"Orden {order_id} actualizada a PAID en DynamoDB")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            error_msg = f"Orden {order_id} no existe en DynamoDB. Debe ser creada por el backend primero."
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
        else:
            print(f"Error actualizando DynamoDB: {str(e)}")
            raise
    except Exception as e:
        print(f"Error actualizando DynamoDB: {str(e)}")
        raise
    
    # 3. Enviar evento ORDER.PAID a EventBridge
    try:
        events.put_events(
            Entries=[{
                'Source': 'kfc.orders',
                'DetailType': 'ORDER.PAID',
                'EventBusName': event_bus,
                'Detail': json.dumps({
                    'orderId': order_id,
                    'paymentId': payment_id
                })
            }]
        )
        print(f"Evento ORDER.PAID enviado a EventBridge para orden {order_id}")
    except Exception as e:
        print(f"Advertencia: No se pudo enviar evento a EventBridge: {str(e)}")
    
    # 4. Retornar datos para el siguiente paso del workflow
    event['status'] = 'PAID'
    event['paymentId'] = payment_id
    return event
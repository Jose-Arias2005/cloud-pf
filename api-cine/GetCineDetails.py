import boto3  # import Boto3
import json
from boto3.dynamodb.conditions import Key  # import Boto3 conditions

def lambda_handler(event, context):
    try:
        # Obtener cinema_id y sala_id desde el cuerpo de la solicitud
        body = event.get('body')
        if isinstance(body, str):  # Si el body es un string, decodificarlo
            body = json.loads(body)

        cinema_id = body.get('cinema_id')  # Obtener cinema_id
        sala_id = body.get('sala_id')  # Obtener sala_id

        if not cinema_id or not sala_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id or sala_id in the request'})
            }

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_salas = dynamodb.Table('t_salas')  # Nombre de la tabla de las salas
        
        # Consultar en la tabla principal con cinema_id y sala_id como claves
        response = t_salas.query(
            KeyConditionExpression=Key('cinema_id').eq(cinema_id) & Key('sala_id').eq(sala_id)
        )

        # Verificar si hay resultados
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Sala not found'})
            }

        # Responder con los detalles de la sala encontrada
        sala_details = response['Items'][0]  # Tomamos el primer elemento, ya que esperamos solo una sala

        # Respuesta con los detalles de la sala
        return {
            'statusCode': 200,
            'body': json.dumps({
                'cinema_id': cinema_id,
                'sala_id': sala_id,
                'sala_details': sala_details  # Los detalles de la sala encontrada
            })
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }

import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        cinema_id = event.get('cinema_id')
        if not cinema_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id in the request'})
            }


        
        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cines = dynamodb.Table('t_cines')  # Nombre dinámico de la tabla

       # Consulta en la tabla principal con cinema_id como clave
        response = t_cines.query(
            KeyConditionExpression=Key('cinema_id').eq(cinema_id)
        )

        # Verificar si hay cines en la respuesta
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No cines encontrados'})
            }

        # Construir la lista de cines con detalles básicos
        cinema_list = []
        for cinema in response['Items']:
            cinema_data = {
                'cinema_id': cinema['cinema_id'],
                'cinema_name': cinema['cinema_name'],
                'address': cinema['address'],
            }
            cinema_list.append(cinema_data)

        # Responder con la lista de cines
        return {
            'statusCode': 200,
            'body': json.dumps(cinema_list)
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

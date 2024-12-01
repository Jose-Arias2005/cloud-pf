import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        # El cuerpo de la solicitud ya es un diccionario, no necesitas json.loads() 
        body = event['body']  # Directamente tomamos el body que es un dict
        cinema_id = body.get('cinema_id')  # Obtener el cinema_id desde el body

        if not cinema_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id in the request'})
            }

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cines = dynamodb.Table('t_cines')  # Nombre de la tabla de cines

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

        # Imprimir el resultado de la consulta para depuración
        print("Cines encontrados:", json.dumps(cinema_list, indent=4))

        # Responder con la lista de cines
        return {
            'statusCode': 200,
            'body': json.dumps(cinema_list, indent=4)
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

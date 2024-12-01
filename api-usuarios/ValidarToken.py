import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Obtener el token del evento
        token = event.get('token')

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_token_acceso')

        # Obtener el token de la tabla
        response = table.get_item(
            Key={
                'token': token  # Buscamos por el token
            }
        )

        # Si el token no existe
        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': json.dumps('Token no existe')
            }

        # Recuperar la fecha de expiración almacenada
        expires_str = response['Item']['expira_en']

        # Convertir la fecha de expiración de string a datetime
        expires = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')

        # Obtener la fecha y hora actuales
        now = datetime.now()

        # Comparar la fecha de expiración con la fecha actual
        if now > expires:
            return {
                'statusCode': 403,
                'body': json.dumps('Token expirado')
            }

        # Si el token es válido
        return {
            'statusCode': 200,
            'body': json.dumps('Token válido')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

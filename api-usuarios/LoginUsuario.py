import boto3
import hashlib
import json

def hash_password(password):
    # Hashear la contraseña con SHA256 (en producción sería mejor usar algo más robusto como bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Manejar diferentes formatos de entrada
        if isinstance(event, str):
            event = json.loads(event)

        # Si el evento tiene un body, tratar de decodificarlo
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                body = event['body'] if isinstance(event['body'], dict) else event
        else:
            body = event

        # Obtener los valores necesarios para el login
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')

        # Verificación de valores
        if not all([cinema_id, user_id, password]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Faltan cinema_id, user_id o password en la solicitud.'
                })
            }

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')

        # Verificar si el usuario existe en la base de datos
        response = table.get_item(
            Key={
                'cinema_id': cinema_id,  # Clave de partición
                'user_id': user_id       # Clave de ordenación
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Usuario no encontrado'
                })
            }

        # Recuperar la contraseña almacenada (hasheada)
        stored_password = response['Item'].get('password')

        # Verificar si la contraseña proporcionada coincide con la almacenada
        if stored_password != hash_password(password):
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'error': 'Contraseña incorrecta'
                })
            }

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login exitoso',
                'role': response['Item'].get('role')
            })
        }

    except Exception as e:
        # Manejo de errores
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Ocurrió un error: {str(e)}'
            })
        }

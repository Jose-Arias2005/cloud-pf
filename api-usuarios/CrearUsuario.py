import boto3
import hashlib
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Manejar diferentes formatos de entrada
        if isinstance(event, str):
            event = json.loads(event)
        
        # Si event es un diccionario con 'body'
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                body = event['body'] if isinstance(event['body'], dict) else event
        else:
            body = event

        # Obtener los valores
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')
        role = body.get('role', 'client')
        
        # Verificación de valores
        if not all([cinema_id, user_id, password]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid request body: missing cinema_id, user_id, or password'
                })
            }
        
        # Validar rol
        valid_roles = ['client', 'admin']
        if role not in valid_roles:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid role. Role must be either "client" or "admin"'
                })
            }
        
        # Hashea la contraseña antes de almacenarla
        hashed_password = hash_password(password)
        
        # Conectar DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_usuarios = dynamodb.Table('t_usuarios')
        
        # Almacena los datos del user en la tabla de usuarios en DynamoDB
        # Asegúrate de que todos los valores sean strings
        t_usuarios.put_item(
            Item={
                'cinema_id': str(cinema_id),
                'user_id': str(user_id),
                'password': hashed_password,
                'role': str(role)
            }
        )
        
        # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User registered successfully',
                'user_id': user_id
            })
        }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

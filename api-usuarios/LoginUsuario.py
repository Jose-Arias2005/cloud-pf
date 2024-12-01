import boto3
import hashlib
import json

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Obtener el cinema_id, user_id y password del evento
        cinema_id = event.get('cinema_id')
        user_id = event.get('user_id')
        password = event.get('password')
        role = event.get('role', 'client')  # Por defecto 'client' si no se pasa

        # Validar que cinema_id, user_id y password estén presentes
        if not cinema_id or not user_id or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id, user_id, or password'})
            }

        # Validar que el rol sea uno de los válidos
        valid_roles = ['client', 'admin']
        if role not in valid_roles:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid role. Must be "client" or "admin"'})
            }

        # Hashear la contraseña antes de almacenarla
        hashed_password = hash_password(password)

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')

        # Verificar si el usuario ya existe en la tabla de usuarios
        response = table.get_item(
            Key={
                'cinema_id': cinema_id,  # partition key
                'user_id': user_id       # sort key
            }
        )

        if 'Item' in response:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'User already exists'})
            }

        # Almacenar los datos del usuario en la tabla de DynamoDB
        table.put_item(
            Item={
                'cinema_id': cinema_id,
                'user_id': user_id,
                'password': hashed_password,
                'role': role
            }
        )

        # Retornar un mensaje de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User registered successfully', 'user_id': user_id})
        }

    except Exception as e:
        # Manejo de excepciones
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

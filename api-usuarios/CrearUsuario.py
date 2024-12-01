import boto3
import hashlib
import json

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        # Obtener el email y el password
        cinema_id = event.get('cinema_id')
        user_id = event.get('user_id')
        password = event.get('password')
        role = event.get('role', 'client')
        
        # Verificar que el email y el password existen
        if user_id and password:
            valid_roles = ['client', 'admin']
            if role not in valid_roles:
                return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid role. Role must be either "client" or "admin"'})
                }
            
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('t_usuarios')
            # Almacena los datos del user en la tabla de usuarios en DynamoDB
            t_usuarios.put_item(
                Item={
                    'cinema_id': cinema_id,
                    'user_id': user_id,
                    'password': hashed_password,
                    'role': role
                }
            )
            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing user_id or password'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }
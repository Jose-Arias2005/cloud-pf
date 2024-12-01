import boto3
import hashlib
import json
import jwt  # Necesitas instalar la librería pyjwt: 'pip install pyjwt'
import datetime

# Función para hashear la contraseña (mejor usar algo más seguro como bcrypt en producción)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para generar un token JWT
def generate_jwt_token(user_id, cinema_id):
    # Definir la clave secreta (debe estar segura y no debe ser pública)
    secret_key = 'mi_clave_secreta'  # Usa una clave segura en producción
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expira en 1 hora

    # Crear el payload del token
    payload = {
        'user_id': user_id,
        'cinema_id': cinema_id,
        'exp': expiration_time  # Fecha de expiración
    }

    # Generar el token JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

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

        # Generar un token JWT
        token = generate_jwt_token(user_id, cinema_id)

        # Almacenar el token en la tabla t_tokens_acceso
        tokens_table = dynamodb.Table('t_tokens_acceso')
        tokens_table.put_item(
            Item={
                'user_id': user_id,
                'cinema_id': cinema_id,
                'token': token,
                'expira_en': str(datetime.datetime.utcnow() + datetime.timedelta(hours=1))  # Fecha de expiración
            }
        )

        # Retornar el token al usuario
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Login exitoso',
                'token': token
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

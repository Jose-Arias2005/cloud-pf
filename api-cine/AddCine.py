import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')

    # Depuración: Imprimir el evento recibido para inspección
    print("Evento recibido:", event)

    # Si el evento tiene un body y es un string, convertirlo a diccionario
    if 'body' in event:
        body = event['body']
        if isinstance(body, str):  # Si el body es un string, decodificarlo
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON in body'})
                }
    else:
        body = event

    # Obtener user_id y cinema_id del cuerpo del evento
    user_id = body.get('user_id')
    cinema_id = body.get('cinema_id')  # Debes asegurarte de tener este campo en el body

    if not user_id or not cinema_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id and cinema_id are required'})
        }

    # Buscar el usuario en la tabla 't_usuarios' usando la clave primaria compuesta
    user_response = t_usuarios.get_item(
        Key={
            'cinema_id': cinema_id,  # Clave de partición
            'user_id': user_id       # Clave de ordenación
        }
    )

    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        }

    role = user_response['Item']['role']

    # Verificar si el usuario tiene permisos de admin
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permiso denegado'})
        }

    # Obtener los datos para crear el cine
    cinema_name = body.get('cinema_name')
    address = body.get('address')
    number_of_halls = body.get('number_of_halls')

    # Validación de entrada
    if not cinema_name or not address or not number_of_halls:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields'})
        }

    # Verificar si el cine ya existe
    existing_cinema = t_cines.get_item(Key={'cinema_id': cinema_id, 'cinema_name': cinema_name})
    if 'Item' in existing_cinema:
        return {
            'statusCode': 409,
            'body': json.dumps({'error': 'Cinema already exists in this district'})
        }

    # Agregar el nuevo cine a la base de datos
    t_cines.put_item(
        Item={
            'cinema_id': cinema_id,
            'cinema_name': cinema_name,
            'address': address,
            'number_of_halls': number_of_halls,
            'created_at': str(int(time.time()))  # Timestamp de creación
        }
    )

    # Respuesta exitosa
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Cinema created successfully'
        })
    }

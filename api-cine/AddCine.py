import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')

    # Depuración: Imprimir el evento recibido para inspección
    print("Evento recibido:", event)

    # Si el evento tiene un body y es un string, convertirlo a diccionario
    body = event.get('body')
    if isinstance(body, str):  # Si el body es un string, decodificarlo
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }

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

    # Verificar si el usuario fue encontrado
    if 'Item' not in user_response:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': f'User with cinema_id: {cinema_id} and user_id: {user_id} not found'})
        }

    # Verificar si el campo 'role' está definido
    role = user_response['Item'].get('role')
    if not role:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Role not defined for this user'})
        }

    # Verificar si el rol es 'admin'
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permiso denegado, solo el admin puede crear un cine'})
        }

    # Si llegamos aquí, el usuario es admin y el rol está definido
    # Continuar con el proceso para crear el cine
    cinema_name = body.get('cinema_name')
    address = body.get('address')
    number_of_halls = body.get('number_of_halls')

    # Validación de entrada para el cine
    if not cinema_name or not address or not number_of_halls:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields for cinema creation'})
        }

    # Verificar si el cine ya existe
    existing_cinema = t_cines.get_item(
        Key={
            'cinema_id': cinema_id,         # Clave de partición
            'cinema_name': cinema_name      # Clave de ordenación
        }
    )
    if 'Item' in existing_cinema:
        return {
            'statusCode': 409,
            'body': json.dumps({'error': 'Cinema already exists'})
        }

    # Agregar el cine a la tabla 't_cines'
    t_cines.put_item(
        Item={
            'cinema_id': cinema_id,
            'cinema_name': cinema_name,
            'address': address,
            'number_of_halls': number_of_halls
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema created successfully'})
    }

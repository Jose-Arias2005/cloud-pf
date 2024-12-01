import boto3
import json

def lambda_handler(event, context):
    print("Evento completo recibido:", event)  # Depuración del evento

    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')

    # Obtener body del evento
    body = event.get('body')
    if isinstance(body, str):  # Si el body es un string, decodificarlo
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }

    print("Cuerpo decodificado:", body)  # Depuración del cuerpo

    # Obtener user_id y cinema_id
    user_id = body.get('user_id')
    cinema_id = body.get('cinema_id')

    if not user_id or not cinema_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id and cinema_id are required'})
        }

    # Consultar el rol del usuario
    user_response = t_usuarios.get_item(Key={'cinema_id': cinema_id, 'user_id': user_id})
    print("Respuesta del usuario:", user_response)  # Depuración de la respuesta de DynamoDB
    
    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        }

    role = user_response['Item']['role']
    
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }

    # Continuar con la creación del cine
    cinema_name = body.get('cinema_name')
    address = body.get('address')
    number_of_halls = body.get('number_of_halls')

    if not cinema_name or not address or not number_of_halls:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields for cinema creation'})
        }

    # Verificar si el cine ya existe
    existing_cinema = t_cines.get_item(
        Key={'cinema_id': cinema_id, 'cinema_name': cinema_name}
    )
    print("Respuesta del cine:", existing_cinema)  # Depuración de la respuesta de DynamoDB
    
    if 'Item' in existing_cinema:
        return {
            'statusCode': 409,
            'body': json.dumps({'error': 'Cinema already exists'})
        }

    # Agregar el cine a la tabla
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

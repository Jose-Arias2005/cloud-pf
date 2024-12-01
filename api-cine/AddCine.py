import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')
    
    # Depuración: Imprime el evento recibido para ver su estructura
    print("Evento recibido:", json.dumps(event))

    # Si el evento tiene un body, cargarlo correctamente
    if 'body' in event:
        try:
            event = json.loads(event['body'])  # Asegúrate de que body sea un diccionario
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid body format'})
            }

    # Obtener user_id
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    user_response = t_usuarios.get_item(Key={'user_id': user_id})
    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        } 
    
    role = user_response['Item']['role']
    
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permiso denegado'})
        }
    
    # Obtener los datos para crear el cine
    cinema_id = event.get('cinema_id')
    cinema_name = event.get('cinema_name')
    address = event.get('address')
    number_of_halls = event.get('number_of_halls')
    
    # Validación de entrada
    if not cinema_id or not cinema_name or not address or not number_of_halls:
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
    
    # Agregar el cine a DynamoDB
    t_cines.put_item(
        Item={
            'cinema_id': cinema_id,
            'cinema_name': cinema_name,
            'address': address,
            'number_of_halls': number_of_halls,
            'created_at': str(int(time.time()))  # Timestamp de creación
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema created successfully'})
    }

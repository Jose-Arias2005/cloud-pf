import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_proyecciones = dynamodb.Table('t_proyecciones')  # Tabla de proyecciones
    t_usuarios = dynamodb.Table('t_usuarios')  # Tabla de usuarios
    t_cines = dynamodb.Table('t_cines')  # Tabla de cines

    # Verificar si el user_id está presente en la solicitud
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }

    try:
        # Consultar rol del usuario
        user_response = t_usuarios.get_item(Key={'user_id': user_id})
        if 'Item' not in user_response or user_response['Item'].get('role') != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Permission denied'})
            }

        # Obtener datos de la proyección desde la solicitud
        cinema_id = event.get('cinema_id')
        cinema_name = event.get('cinema_name')
        show_id = event.get('show_id')
        title = event.get('title')
        hall = event.get('hall')
        seats_available = event.get('seats_available', 50) 
        date = event.get('date')
        start_time = event.get('start_time')
        end_time = event.get('end_time')

        # Validar campos obligatorios
        if not all([cinema_id, cinema_name, show_id, title, hall, date, start_time, end_time]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Verificar si el cine existe
        cinema_response = t_cines.get_item(Key={'cinema_id': cinema_id, 'cinema_name': cinema_name})
        if 'Item' not in cinema_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Cinema not found'})
            }

        # Verificar si la proyección existe
        existing_function = t_proyecciones.get_item(Key={'cinema_id': cinema_id, 'cinema_name': cinema_name, 'show_id': show_id})
        if 'Item' in existing_function:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'Projection already exists'})
            }

        # Agregar nueva proyección a DynamoDB
        t_proyecciones.put_item(
            Item={
                'cinema_id': cinema_id,
                'cinema_name': cinema_name,
                'show_id': show_id,
                'title': title,
                'hall': hall,
                'seats_available': seats_available,
                'date': date,
                'start_time': start_time,
                'end_time': end_time
            }
        )

        # Respuesta exitosa
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Showtime added successfully',
                'show_details': {
                    'cinema_id': cinema_id,
                    'cinema_name': cinema_name,
                    'show_id': show_id,
                    'title': title,
                    'hall': hall,
                    'seats_available': seats_available,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time
                }
            })
        }

    except Exception as e:
        # Manejo de excepciones
        print(f"Exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

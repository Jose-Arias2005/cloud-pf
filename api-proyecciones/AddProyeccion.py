import boto3
import json

def lambda_handler(event, context):
    try:
        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_proyecciones = dynamodb.Table('t_proyecciones')  # Tabla de proyecciones
        t_usuarios = dynamodb.Table('t_usuarios')  # Tabla de usuarios
        t_cines = dynamodb.Table('t_cines')  # Tabla de cines

        # Obtener los datos del cuerpo de la solicitud
        body = event['body']  # Usar event['body'] directamente ya que se pasa como un diccionario o JSON válido
        # Si el body es un string, entonces parsearlo
        if isinstance(body, str):
            body = json.loads(body)

        # Obtener los datos de la proyección
        cinema_id = body.get('cinema_id')
        cinema_name = body.get('cinema_name')
        show_id = body.get('show_id')
        title = body.get('title')
        hall = body.get('hall')
        seats_available = body.get('seats_available', 50)  # Default 50
        date = body.get('date')
        start_time = body.get('start_time')
        end_time = body.get('end_time')

        # Validar campos obligatorios
        requiredFields = ['cinema_id', 'cinema_name', 'show_id', 'title', 'hall', 'date', 'start_time', 'end_time']
        missing_fields = [field for field in requiredFields if not body.get(field)]
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Missing required fields: {", ".join(missing_fields)}'})
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

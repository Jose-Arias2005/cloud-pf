import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')

    # Obtener el cuerpo del evento y decodificarlo si es un string
    body = event.get('body')
    if isinstance(body, str):  # Si el body es un string, decodificarlo
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }

    # Obtener user_id y cinema_id desde el cuerpo del evento
    user_id = body.get('user_id')
    cinema_id = body.get('cinema_id')

    if not user_id or not cinema_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id and cinema_id are required'})
        }

    # Consultar el rol del usuario
    try:
        # Usar tanto cinema_id como user_id en la consulta
        user_response = t_usuarios.get_item(
            Key={'cinema_id': cinema_id, 'user_id': user_id}  # Consulta por clave primaria compuesta
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error querying user data: {str(e)}'})
        }

    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        }
    
    role = user_response['Item']['role']
    
    # Verificar permisos (solo admin puede eliminar cines)
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }

    # Obtener cinema_id y cinema_name directamente del evento
    cinema_name = body.get('cinema_name')
    
    # Validación de entrada
    if not cinema_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_name is required'})
        }

    # Verificar si el cine existe antes de eliminar
    try:
        existing_cinema = t_cines.get_item(
            Key={'cinema_id': cinema_id, 'cinema_name': cinema_name}
        )
        if 'Item' not in existing_cinema:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Cinema not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error checking cinema existence: {str(e)}'})
        }

    # Eliminar el cine
    try:
        t_cines.delete_item(
            Key={'cinema_id': cinema_id, 'cinema_name': cinema_name}
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error deleting cinema: {str(e)}'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema deleted successfully'})
    }

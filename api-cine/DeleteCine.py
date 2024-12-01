import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')
    
    # Obtener user_id
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    # Consultar el rol del usuario
    try:
        user_response = t_usuarios.get_item(Key={'user_id': user_id})
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
    cinema_id = event.get('cinema_id')
    cinema_name = event.get('cinema_name')
    
    # Validación de entrada
    if not cinema_id or not cinema_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and cinema_name are required'})
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

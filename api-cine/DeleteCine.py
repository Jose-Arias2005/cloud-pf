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
    user_response = t_usuarios.get_item(Key={'user_id': user_id})
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
    
    # Obtener cinema_id y district directamente del evento
    cinema_id = event.get('cinema_id')
    cinema_name = event.get('cinema_name')
    
    # Validación de entrada
    if not cinema_id or not cinema_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and cinema_name are required'})
        }
    
    # Eliminar el cine
    t_cines.delete_item(
        Key={'cinema_id': cinema_id, 'cinema_name': cinema_name}
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema deleted successfully'})
    }

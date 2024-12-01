import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')  # Nombre dinámico de la tabla de cines
    t_usuarios = dynamodb.Table('t_usuarios')  # Nombre dinámico de la tabla de usuarios
    
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
    
    # Verificar permisos (solo admin puede actualizar cines)
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }
    
    # Obtener los datos para actualizar el cine
    cinema_id = event.get('cinema_id')
    cinema_name = event.get('cinema_name')
    address = event.get('address')
    number_of_halls = event.get('number_of_halls')

    # Construir expresiones de actualización
    update_expression = "SET "
    expression_values = {}
    expression_attribute_names = {}  # Almacenar los alias de nombres de atributos reservados
    
    if cinema_name:
        update_expression += "#nm = :cinema_name, "  # Alias para "cinema_name"
        expression_values[":cinema_name"] = cinema_name
        expression_attribute_names["#nm"] = "cinema_name"  # Alias que sustituye "cinema_name"
    if address:
        update_expression += "address = :address, "
        expression_values[":address"] = address
    if number_of_halls:
        update_expression += "number_of_halls = :number_of_halls, "
        expression_values[":number_of_halls"] = number_of_halls

    # Remover la última coma y espacio de update_expression
    update_expression = update_expression.rstrip(', ')
    
    # Verificar si hay algo que actualizar
    if not expression_values:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No fields to update'})
        }

    # Ejecutar la actualización
    t_cines.update_item(
        Key={'cinema_id': cinema_id},  # Asegúrate de usar solo la clave primaria adecuada
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_attribute_names  # Agregar los alias aquí
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema updated successfully'})
    }

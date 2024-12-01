import boto3
import json

def lambda_handler(event, context):
    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    t_proyecciones = dynamodb.Table('t_proyecciones')
    t_cines = dynamodb.Table('t_cines')
        
    # Obtener los identificadores clave
    cinema_id = event.get('cinema_id')
    cinema_name = event.get('cinema_name')
    show_id = event.get('show_id')
    
    if not cinema_id or not cinema_name or not show_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and show_id are required'})
        }

    # Verificar si el cine existe en la tabla t_cines
    cinema_response = t_cines.get_item(Key={'cinema_id': cinema_id})
    if 'Item' not in cinema_response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Cinema not found'})
        }

    # Construir la expresión de actualización con los campos en el body
    update_expression = "SET "
    expression_values = {}
    expression_names = {}  # Inicializar como un diccionario vacío

    # Campos para actualizar
    fields_to_update = ['cinema_id','cinema_name','show_id', 'hall', 'start_time', 'end_time']

    for field in fields_to_update:
        if event.get(field) is not None:
            # Usar alias si el nombre del campo es reservado
            if field == 'name':
                expression_names['#nm'] = field
                update_expression += "#nm = :name, "
                expression_values[":name"] = event[field]
            else:
                update_expression += f"{field} = :{field}, "
                expression_values[f":{field}"] = event[field]

    # Remover la última coma y espacio de update_expression
    update_expression = update_expression.rstrip(', ')

    if not expression_values:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No fields to update'})
        }


    update_params = {
        'Key': {'cinema_id': cinema_id,'cinema_name': cinema_name, 'show_id': show_id},
        'UpdateExpression': update_expression,
        'ExpressionAttributeValues': expression_values
    }
    if expression_names:  # Solo incluir si hay alias definidos
        update_params['ExpressionAttributeNames'] = expression_names

    t_proyecciones.update_item(**update_params)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Showtime updated successfully'})
    }

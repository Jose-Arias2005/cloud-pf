const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.detalleCompra = async (event) => {
    try {
        const { user_id, date } = JSON.parse(event.body);

        if (!user_id || !date) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id y date son obligatorios.' }),
            };
        }

        const response = await dynamodb
            .query({
                TableName: process.env.TABLE_NAME_VISITAS,
                KeyConditionExpression: 'user_id = :user_id AND date = :date',
                ExpressionAttributeValues: {
                    ':user_id': user_id,
                    ':date': date,
                },
            })
            .promise();

        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron visitas para el usuario en la fecha especificada.' }),
            };
        }

        // Si se encuentran visitas, retornarlas en la respuesta
        return {
            statusCode: 200,
            body: JSON.stringify(response.Items),
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Error interno del servidor',
                details: error.message,
            }),
        };
    }
};

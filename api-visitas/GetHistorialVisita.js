const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.consultarHistorial = async (event) => {
    try {
        const { user_id } = JSON.parse(event.body);

        if (!user_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id es obligatorio.' }),
            };
        }

        const response = await dynamodb
            .query({
                TableName: process.env.TABLE_NAME_VISITAS,
                KeyConditionExpression: 'user_id = :user_id',
                ExpressionAttributeValues: {
                    ':user_id': user_id,
                },
            })
            .promise();

        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron visitas para este usuario.' }),
            };
        }

        return {
            statusCode: 200,
            body: JSON.stringify(response.Items),
        };
    } catch (error) {
        console.error('Error al consultar el historial:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Error interno al consultar el historial de visitas.',
                details: error.message,
            }),
        };
    }
};

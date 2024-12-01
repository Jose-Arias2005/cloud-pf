const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Verificar si el body es un string, en cuyo caso lo parseamos
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body); // Si es un string, lo parseamos a objeto
        }

        const { title, cinema_id } = body;

        const requiredFields = ['cinema_id', 'title'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({ error: `Falta el campo obligatorio: ${field}` }),
                };
            }
        }

        // Eliminar la película (utilizando cinema_id y title como claves)
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        await dynamodb
            .delete({
                TableName: t_peliculas,
                Key: { cinema_id, title },  // Usamos ambas claves
            })
            .promise();

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Película eliminada correctamente' }),
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error interno del servidor', details: error.message }),
        };
    }
};

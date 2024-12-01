const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, title, cinema_id } = body;

        const requiredFields = ['user_id', 'cinema_id', 'title'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                statusCode: 400,
                body: JSON.stringify({ error: `Falta el campo obligatorio: ${field}` }),
                };
            }
        }

        // Verificar permisos del usuario
        const t_usuarios = process.env.TABLE_NAME_USUARIOS;
        const userResponse = await dynamodb
            .get({
                TableName: t_usuarios,
                Key: { user_id },
            })
            .promise();

        // Verificar permisos del usuario y si el cinema_id del usuario coincide con el cinema_id del cuerpo de la solicitud
        if (!userResponse.Item || userResponse.Item.role !== 'admin' || userResponse.Item.cinema_id !== cinema_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Permiso denegado o el usuario no tiene acceso a este cine' }),
            };
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

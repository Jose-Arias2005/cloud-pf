const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        // Parsear el body de la solicitud
        const body = JSON.parse(event.body); 
        const { user_id, cinema_id, title, genre, duration, rating } = body;

        // Validar que todos los campos requeridos estén presentes
        const requiredFields = ['user_id', 'cinema_id', 'title', 'genre', 'duration', 'rating'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({ error: `Falta el campo obligatorio: ${field}` }),
                };
            }
        }

        // Conectar a DynamoDB y verificar si el usuario tiene permisos
        const t_usuarios = process.env.TABLE_NAME_USUARIOS;
        const userResponse = await dynamodb.get({
            TableName: t_usuarios,
            Key: { user_id },
        }).promise();

        // Verificar si el usuario existe y si tiene permisos de 'admin'
        if (!userResponse.Item || userResponse.Item.role !== 'admin' || userResponse.Item.cinema_id !== cinema_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Permiso denegado' }),
            };
        }

        // Verificar si la película ya existe en la tabla de películas
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        const existingMovie = await dynamodb.get({
            TableName: t_peliculas,
            Key: { cinema_id, title },
        }).promise();

        // Si la película ya existe, devolver error
        if (existingMovie.Item) {
            return {
                statusCode: 409,
                body: JSON.stringify({ error: 'La película ya existe' }),
            };
        }

        // Si no existe, agregar la nueva película
        await dynamodb.put({
            TableName: t_peliculas,
            Item: { cinema_id, title, genre, duration, rating },
        }).promise();

        // Respuesta exitosa
        return {
            statusCode: 201,
            body: JSON.stringify({ message: 'Película agregada correctamente' }),
        };

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error interno del servidor', details: error.message }),
        };
    }
};

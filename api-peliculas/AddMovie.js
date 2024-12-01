const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, cinema_id, title, genre, duration, rating} = body;  // Añadir cinema_id

        // Validar entrada
        const requiredFields = ['user_id', 'cinema_id', 'title', 'genre', 'duration', 'rating'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                statusCode: 400,
                body: JSON.stringify({ error: Falta el campo obligatorio: ${field} }),
                };
            }
        }
        

        // Conectar a la tabla de usuarios
        const t_usuarios = process.env.TABLE_NAME_USUARIOS;
        const userResponse = await dynamodb
            .get({
                TableName: t_usuarios,
                Key: { user_id },
            })
            .promise();

        if (!userResponse.Item || userResponse.Item.role !== 'admin' || userResponse.Item.cinema_id !== cinema_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({
                    error: !userResponse.Item ? 'Permiso denegado' : 'El usuario no tiene acceso a este cine',
                }),
            };
        }

        // Conectar a la tabla de películas y verificar si ya existe la película
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        const existingMovie = await dynamodb
            .get({
                TableName: t_peliculas,
                Key: { cinema_id, title },  // Usar cinema_id y title como claves primarias
            })
            .promise();

        if (existingMovie.Item) {
            return {
                statusCode: 409,
                body: JSON.stringify({ error: 'La película ya existe' }),
            };
        }

        // Agregar la nueva película
        await dynamodb
            .put({
                TableName: t_peliculas,
                Item: {
                    cinema_id,
                    title,
                    genre,
                    duration,
                    rating,
                },
            })
            .promise();

        return {
            statusCode: 201,
            body: JSON.stringify({ message: 'Película agregada correctamente' }),
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

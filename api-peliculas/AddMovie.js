const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Verifica si el cuerpo está en formato JSON o ya es un objeto
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body); // Si es una cadena, parsearlo
        }



        
        const { user_id, cinema_id, title, genre, duration, rating } = body;

        // Validar entrada
        const requiredFields = ['cinema_id', 'title', 'genre', 'duration', 'rating'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({ error: `Falta el campo obligatorio: ${field}` }),
                };
            }
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

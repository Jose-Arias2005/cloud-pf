const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, cinema_id, title, genre, duration, rating } = body;

        // Validar campos obligatorios
        const requiredFields = ['user_id', 'title', 'cinema_id'];
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
                Key: { cinema_id, user_id },  // La clave primaria de la tabla usuarios es cinema_id + user_id
            })
            .promise();

        if (!userResponse.Item || userResponse.Item.role !== 'admin') {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Permiso denegado: el usuario no tiene acceso como admin' }),
            };
        }

        // Verificar que el cinema_id del usuario coincida con el cinema_id del cuerpo de la solicitud
        if (userResponse.Item.cinema_id !== cinema_id) {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'El usuario no tiene acceso a este cine' }),
            };
        }

        // Consultar si la película ya existe en la tabla de Películas (con el cinema_id y el title)
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        const movieResponse = await dynamodb
            .get({
                TableName: t_peliculas,
                Key: { cinema_id, title },  // La clave primaria de la tabla películas es cinema_id + title
            })
            .promise();

        if (movieResponse.Item) {
            return {
                statusCode: 409,
                body: JSON.stringify({ error: 'La película ya existe' }),
            };
        }

        // Agregar la nueva película a la tabla Películas
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

        // Responder con éxito
        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Película agregada exitosamente' }),
        };

    } catch (error) {
        console.error("Error:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error interno del servidor', details: error.message }),
        };
    }
};

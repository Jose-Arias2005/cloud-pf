const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Obtener el cinema_id desde el cuerpo de la solicitud
        const body = JSON.parse(event.body);  // Asegúrate de que el cuerpo sea JSON
        const cinema_id = body.cinema_id;

        // Validar si el cinema_id está presente en el cuerpo
        if (!cinema_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Missing cinema_id in the request' })
            };
        }

        const tableName = `t_peliculas`;

        // Consultar todas las películas para el cinema_id
        const params = {
            TableName: tableName,
            KeyConditionExpression: 'cinema_id = :cinema_id',
            ExpressionAttributeValues: {
                ':cinema_id': cinema_id
            },
            ExclusiveStartKey: event.queryStringParameters?.lastEvaluatedKey || null,  // Paginación si es necesario
        };

        const response = await dynamodb.query(params).promise();

        // Verificar si hay películas
        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron películas para este cine' })
            };
        }

        // Formatear la lista de películas
        const moviesList = response.Items.map(movie => ({
            cinema_id: movie.cinema_id,
            title: movie.title,
            genre: movie.genre,
            duration: movie.duration,
            rating: movie.rating
        }));

        // Responder con la lista de películas
        return {
            statusCode: 200,
            body: JSON.stringify(moviesList)
        };

    } catch (error) {
        console.error("Exception:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Internal server error',
                details: error.message
            })
        };
    }
};

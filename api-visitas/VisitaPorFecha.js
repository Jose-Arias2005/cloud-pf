const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.filtrarvisitas = async (event) => {
    try {
        const { user_id, start_date, end_date } = JSON.parse(event.body);

        if (!user_id || !start_date || !end_date) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id, start_date y end_date son obligatorios.' }),
            };
        }

        // Consultar las visitas del usuario en el rango de fechas especificado
        const visitasResponse = await dynamodb.query({
            TableName: process.env.TABLE_NAME_VISITAS,
            KeyConditionExpression: 'user_id = :user_id AND date BETWEEN :start_date AND :end_date',
            ExpressionAttributeValues: {
                ':user_id': user_id,
                ':start_date': start_date,
                ':end_date': end_date,
            },
        }).promise();

        // Verificar si existen visitas en el rango de fechas
        if (!visitasResponse.Items || visitasResponse.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron visitas en el rango de fechas especificado.' }),
            };
        }

        // Extraer los show_id de las visitas encontradas
        const showIds = visitasResponse.Items.map(compra => compra.show_id);

        // Si no se encontraron show_ids, retornar un error
        if (showIds.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron show_id asociados a este usuario.' }),
            };
        }

        // Ahora, consultar las proyecciones usando los show_id encontrados
        const proyeccionesResponse = await dynamodb.query({
            TableName: process.env.TABLE_NAME_PROYECCIONES, // Tabla de proyecciones
            IndexName: 'show_id-index', // Asumiendo que hay un índice global para show_id
            KeyConditionExpression: 'show_id IN (:show_ids)',
            ExpressionAttributeValues: {
                ':show_ids': dynamodb.createSet(showIds), // Utilizamos createSet para manejar múltiples valores
            },
        }).promise();

        // Verificar si existen proyecciones para los show_ids
        if (!proyeccionesResponse.Items || proyeccionesResponse.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron proyecciones para los show_ids especificados.' }),
            };
        }

        // Filtrar las proyecciones que están dentro del rango de fechas (por ejemplo, la fecha de la proyección)
        const proyeccionesFiltradas = proyeccionesResponse.Items.filter(proyeccion => {
            const proyeccionDate = new Date(proyeccion.date);
            return proyeccionDate >= new Date(start_date) && proyeccionDate <= new Date(end_date);
        });

        return {
            statusCode: 200,
            body: JSON.stringify(proyeccionesFiltradas),
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

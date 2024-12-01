const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const dynamoDB = new AWS.DynamoDB.DocumentClient();
module.exports.reservarAsientos = async (event) => {
    try {
        const { 
            cinema_id, 
            cinema_name, 
            show_id, 
            seats_reserved
        } = JSON.parse(event.body);

        if (!cinema_id || !cinema_name || !show_id || !seats_reserved) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Missing required fields' })
            };
        }

        const getParams = {
            TableName: `t_proyecciones`,
            Key: { 
                cinema_id: cinema_id,
                cinema_name: cinema_name,
                show_id: show_id,
            }
        };

        const existingShow = await dynamoDB.get(getParams).promise();

        if (!existingShow.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Show not found' })
            };
        }

        const currentSeatsAvailable = existingShow.Item.seats_available || 0;
        if (currentSeatsAvailable < seats_reserved) {
            return {
                statusCode: 400,
                body: JSON.stringify({ 
                    error: 'Not enough seats available',
                    seats_available: currentSeatsAvailable 
                })
            };
        }

        const updateParams = {
            TableName: `t_proyecciones`,
            Key: { 
                cinema_id: cinema_id, 
                cinema_name: cinema_name,
                show_id: show_id 
            },
            UpdateExpression: 'SET seats_available = seats_available - :seats_reserved',
            ConditionExpression: 'seats_available >= :seats_reserved',
            ExpressionAttributeValues: {
                ':seats_reserved': seats_reserved
            },
            ReturnValues: 'ALL_NEW'
        };

        const updatedShow = await dynamoDB.update(updateParams).promise();

        const responseBody = {
            cinema_id: existingShow.Item.cinema_id,
            cinema_name: existingShow.Item.cinema_name,
            show_id: existingShow.Item.show_id,
            title: existingShow.Item.title,
            hall: existingShow.Item.hall,
            date: existingShow.Item.date,
            seats_reserved: seats_reserved,
            seats_available: updatedShow.Attributes.seats_available,
            start_time: existingShow.Item.start_time,
            end_time: existingShow.Item.end_time
        };

        return {
            statusCode: 200,
            body: JSON.stringify(responseBody)
        };

    } catch (error) {
        console.error('Reservation error:', error);

        return {
            statusCode: 500,
            body: JSON.stringify({ 
                error: 'Internal server error', 
                details: error.message 
            })
        };
    }
};
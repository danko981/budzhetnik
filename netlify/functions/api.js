const axios = require('axios');

// Прокси-функция для API
exports.handler = async function (event, context) {
    // URL API сервера, который можно заменить на URL вашего сервера
    const API_URL = process.env.API_URL || 'https://budgetnik-api.herokuapp.com';

    try {
        // Получаем путь API из URL
        const path = event.path.replace('/.netlify/functions/api', '');

        // Полный URL для запроса
        const url = `${API_URL}${path}`;

        // Копируем заголовки запроса, но удаляем некоторые специфичные для Netlify
        const headers = { ...event.headers };
        delete headers.host;
        delete headers.connection;

        // Выполняем запрос к API серверу
        const response = await axios({
            method: event.httpMethod,
            url: url,
            data: event.body,
            headers: headers,
        });

        // Возвращаем ответ клиенту
        return {
            statusCode: response.status,
            body: JSON.stringify(response.data),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            },
        };
    } catch (error) {
        // Обработка ошибки
        console.error('API Error:', error);

        return {
            statusCode: error.response?.status || 500,
            body: JSON.stringify({
                message: 'Ошибка при обращении к API',
                error: error.response?.data || error.message,
            }),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
        };
    }
}; 
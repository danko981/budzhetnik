let axios;
try {
    axios = require('axios');
} catch (error) {
    console.error('Error loading axios module:', error.message);
    // Отправляем ошибку, если модуль не загружен
    exports.handler = async function (event, context) {
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'API Server Error: dependency not loaded',
                error: 'axios module could not be loaded'
            }),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        };
    };
    return;
}

// Прокси-функция для API
exports.handler = async function (event, context) {
    // URL API сервера
    const API_URL = process.env.API_URL || 'https://api.budzhetnik.ru';

    // Обработка предварительных запросов OPTIONS для CORS
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Max-Age': '86400'
            },
            body: ''
        };
    }

    try {
        // Получаем путь API из URL
        const path = event.path.replace('/.netlify/functions/api', '');

        // Полный URL для запроса
        const url = `${API_URL}${path}`;

        // Копируем заголовки запроса, но удаляем некоторые специфичные для Netlify
        const headers = { ...event.headers };
        delete headers.host;
        delete headers.connection;
        delete headers['content-length'];
        delete headers['user-agent'];
        delete headers['cloud-front-forwarded-proto'];

        console.log(`Making ${event.httpMethod} request to: ${url}`);

        // Обработка тела запроса
        let requestBody;
        try {
            requestBody = event.body ? JSON.parse(event.body) : null;
        } catch (error) {
            requestBody = event.body;
        }

        // Выполняем запрос к API серверу
        const response = await axios({
            method: event.httpMethod,
            url: url,
            data: requestBody,
            headers: headers,
            validateStatus: () => true // Разрешаем любые статусы ответов
        });

        console.log(`Response status: ${response.status}`);

        // Возвращаем ответ клиенту
        return {
            statusCode: response.status,
            body: JSON.stringify(response.data),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            },
        };
    } catch (error) {
        // Подробная регистрация ошибки
        console.error('API Error:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response headers:', error.response.headers);
            console.error('Response data:', error.response.data);
        } else if (error.request) {
            console.error('No response received:', error.request);
        }

        return {
            statusCode: error.response?.status || 500,
            body: JSON.stringify({
                message: 'Ошибка при обращении к API',
                error: error.response?.data || error.message,
                path: event.path,
                method: event.httpMethod
            }),
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            },
        };
    }
}; 
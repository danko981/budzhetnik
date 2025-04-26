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

// Тестовые учетные данные для локальной разработки
const TEST_USERS = [
    { id: 1, username: 'demo', password: 'demo123', email: 'demo@example.com' },
    { id: 2, username: 'test', password: 'test123', email: 'test@example.com' }
];

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

    // Особая обработка для логина - имитация API сервера для тестов
    if ((event.path.endsWith('/auth/login') || event.path.endsWith('/api/v1/auth/login')) && event.httpMethod === 'POST') {
        console.log('Processing login request directly in the function');
        console.log('Request path:', event.path);

        try {
            const body = JSON.parse(event.body);

            // Проверка обязательных полей
            if (!body.username || !body.password) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({
                        message: 'Необходимо указать имя пользователя и пароль'
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            }

            // Поиск пользователя в тестовых данных
            const user = TEST_USERS.find(
                u => u.username === body.username && u.password === body.password
            );

            if (!user) {
                return {
                    statusCode: 401,
                    body: JSON.stringify({
                        message: 'Неверное имя пользователя или пароль'
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            }

            // Генерация фиктивного токена
            const dummyToken = `test.${Buffer.from(JSON.stringify({ id: user.id, username: user.username })).toString('base64')}.token`;

            // Имитация успешной авторизации
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Авторизация успешна',
                    user: {
                        id: user.id,
                        username: user.username,
                        email: user.email
                    },
                    token: dummyToken
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                }
            };
        } catch (error) {
            console.error('Error processing login request:', error);
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: 'Ошибка при обработке запроса на авторизацию',
                    error: error.message
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                }
            };
        }
    }

    // Особая обработка для регистрации - имитация API сервера для тестов
    if ((event.path.endsWith('/auth/register') || event.path.endsWith('/api/v1/auth/register')) && event.httpMethod === 'POST') {
        console.log('Processing register request directly in the function');
        console.log('Request path:', event.path);

        try {
            const body = JSON.parse(event.body);

            // Проверка обязательных полей
            if (!body.username || !body.password || !body.email) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({
                        message: 'Необходимо указать имя пользователя, пароль и email'
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            }

            // Имитация успешной регистрации
            return {
                statusCode: 201,
                body: JSON.stringify({
                    message: 'Пользователь успешно зарегистрирован',
                    user: {
                        id: 2, // ID для нового пользователя
                        username: body.username,
                        email: body.email
                    }
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                }
            };
        } catch (error) {
            console.error('Error processing register request:', error);
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: 'Ошибка при обработке запроса на регистрацию',
                    error: error.message
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                }
            };
        }
    }

    // Особая обработка для получения данных пользователя - имитация API сервера для тестов
    if ((event.path.endsWith('/auth/me') || event.path.endsWith('/api/v1/auth/me')) && event.httpMethod === 'GET') {
        console.log('Processing get user info request directly in the function');
        console.log('Request path:', event.path);

        try {
            // Проверяем токен
            const authHeader = event.headers.authorization || '';
            const token = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : null;

            if (!token || !token.startsWith('test.')) {
                return {
                    statusCode: 401,
                    body: JSON.stringify({
                        message: 'Требуется авторизация'
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            }

            // Пытаемся расшифровать токен для получения информации о пользователе
            try {
                const tokenParts = token.split('.');
                if (tokenParts.length !== 3) {
                    throw new Error('Invalid token format');
                }

                const payload = JSON.parse(Buffer.from(tokenParts[1], 'base64').toString());
                const userId = payload.id;

                // Находим пользователя по ID
                const user = TEST_USERS.find(u => u.id === userId);
                if (!user) {
                    throw new Error('User not found');
                }

                return {
                    statusCode: 200,
                    body: JSON.stringify({
                        id: user.id,
                        username: user.username,
                        email: user.email
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            } catch (error) {
                return {
                    statusCode: 401,
                    body: JSON.stringify({
                        message: 'Недействительный токен'
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    }
                };
            }
        } catch (error) {
            console.error('Error processing user info request:', error);
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: 'Ошибка при обработке запроса на получение данных пользователя',
                    error: error.message
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                }
            };
        }
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
            console.log('Request body:', JSON.stringify(requestBody));
        } catch (error) {
            requestBody = event.body;
            console.log('Raw request body:', event.body);
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
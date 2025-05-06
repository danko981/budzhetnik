// Настройки для фронтенда
window.apiConfig = {
    apiUrl: 'http://localhost:8000/api/v1',
    authEndpoint: 'http://localhost:8000/api/v1/auth',
    timeout: 60000, // 60 секунд
    retryAttempts: 5,
    useSimpleApi: true // Флаг для использования упрощенного API
}; 
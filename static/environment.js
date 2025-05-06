// Настройки для фронтенда
window.apiConfig = {
    apiUrl: '/api/v1',
    authEndpoint: '/api/v1/auth',
    timeout: 120000, // 120 секунд - увеличиваем тайм-аут
    retryAttempts: 5,
    useSimpleApi: true // Флаг для использования упрощенного API
}; 
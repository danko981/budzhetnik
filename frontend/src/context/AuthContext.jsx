import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

// Создаем контекст авторизации
const AuthContext = createContext();

// Тестовые учетные данные для локальной разработки
const TEST_USERS = [
    { id: 1, username: 'demo', password: 'demo123', email: 'demo@example.com' },
    { id: 2, username: 'test', password: 'test123', email: 'test@example.com' }
];

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Проверка наличия токена при загрузке
    useEffect(() => {
        const checkToken = async () => {
            // Пробуем сначала получить access_token (новый формат), затем token (старый формат)
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const response = await api.get('/api/v1/auth/me');
                if (response.data) {
                    setUser(response.data);
                    setIsAuthenticated(true);
                }
            } catch (err) {
                // Удаляем оба формата токенов при ошибке
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('token');
                console.error('Error verifying token:', err);
            } finally {
                setLoading(false);
            }
        };

        checkToken();
    }, []);

    // Функция для входа пользователя
    const login = async (credentials) => {
        try {
            setError(null);
            setLoading(true);

            // Делаем запрос к API
            const response = await api.post('/api/v1/auth/login', credentials);

            console.log('Login response:', response.data); // Для диагностики

            // Проверяем наличие access_token (новый формат) или token (старый формат)
            if (response.data && (response.data.access_token || response.data.token)) {
                // Сохраняем токены по новому формату
                if (response.data.access_token) {
                    localStorage.setItem('access_token', response.data.access_token);

                    // Если есть refresh_token, тоже сохраняем
                    if (response.data.refresh_token) {
                        localStorage.setItem('refresh_token', response.data.refresh_token);
                    }
                }
                // Для совместимости со старым форматом
                else if (response.data.token) {
                    localStorage.setItem('token', response.data.token);
                    localStorage.setItem('access_token', response.data.token); // Для совместимости с новым кодом
                }

                // Сохраняем данные пользователя
                if (response.data.user) {
                    setUser(response.data.user);
                }

                setIsAuthenticated(true);
                return { success: true };
            } else {
                throw new Error('Токен не был получен от сервера');
            }
        } catch (error) {
            console.error('Login error:', error);

            let errorMessage = 'Ошибка при авторизации';

            // Обработка разных типов ошибок
            if (error.response) {
                if (error.response.status === 401) {
                    errorMessage = 'Неверное имя пользователя или пароль';
                } else if (error.response.status === 400) {
                    errorMessage = 'Заполните все необходимые поля';
                } else if (error.response.status === 500) {
                    errorMessage = 'Ошибка сервера. Пожалуйста, попробуйте позже';
                }
            } else if (error.request) {
                errorMessage = 'Не удалось связаться с сервером. Проверьте интернет-соединение';
            }

            setError(errorMessage);
            return { success: false, message: errorMessage };
        } finally {
            setLoading(false);
        }
    };

    // Функция для регистрации пользователя
    const register = async (userData) => {
        try {
            setError(null);
            setLoading(true);

            // Проверяем, существует ли пользователь с таким же именем в тестовых данных
            if (process.env.NODE_ENV === 'development') {
                const userExists = TEST_USERS.some(user => user.username === userData.username);
                if (userExists) {
                    return {
                        success: false,
                        message: 'Пользователь с таким именем уже существует'
                    };
                }
            }

            // Отправляем запрос на регистрацию
            const response = await api.post('/api/v1/auth/register', userData);
            return {
                success: true,
                message: 'Регистрация успешна. Теперь вы можете войти.'
            };
        } catch (error) {
            console.error('Registration error:', error);

            let errorMessage = 'Ошибка при регистрации';

            // Обработка разных типов ошибок
            if (error.response) {
                if (error.response.status === 400) {
                    errorMessage = error.response.data.message || 'Некорректные данные';
                } else if (error.response.status === 409) {
                    errorMessage = 'Пользователь с таким именем уже существует';
                } else if (error.response.status === 500) {
                    errorMessage = 'Ошибка сервера. Пожалуйста, попробуйте позже';
                } else if (error.response.status === 404) {
                    errorMessage = 'Сервис регистрации недоступен. Пожалуйста, попробуйте позже';
                }
            } else if (error.request) {
                errorMessage = 'Не удалось связаться с сервером. Проверьте интернет-соединение';
            }

            setError(errorMessage);
            return { success: false, message: errorMessage };
        } finally {
            setLoading(false);
        }
    };

    // Функция для выхода пользователя
    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token'); // Удаляем и старый формат для совместимости
        setUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isAuthenticated,
                loading,
                error,
                login,
                register,
                logout,
                testUsers: TEST_USERS
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

// Хук для использования контекста авторизации
export const useAuth = () => useContext(AuthContext); 
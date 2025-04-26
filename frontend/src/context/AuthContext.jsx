import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Проверяем, есть ли токен
        const token = localStorage.getItem('token');
        if (token) {
            // Установка токена для запросов
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            checkAuthState();
        } else {
            setIsLoading(false);
        }
    }, []);

    const checkAuthState = async () => {
        try {
            // Проверяем валидность токена и получаем данные пользователя
            const response = await api.get('/api/v1/auth/me');
            setCurrentUser(response.data);
            setIsAuthenticated(true);
        } catch (err) {
            console.error('Auth check failed:', err);
            logout(); // Если ошибка, выходим
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (credentials) => {
        setError(null);
        try {
            const response = await api.post('/api/v1/auth/login', credentials);

            // Если API возвращает JWT токен и данные пользователя
            if (response.data && response.data.access_token) {
                const { access_token, user } = response.data;

                // Сохраняем токен
                localStorage.setItem('token', access_token);
                api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

                setCurrentUser(user);
                setIsAuthenticated(true);
                return true;
            } else {
                throw new Error('Неверный ответ от сервера');
            }
        } catch (err) {
            console.error('Login failed:', err);
            setError(err.response?.data?.message || 'Ошибка входа. Проверьте данные и попробуйте снова.');
            return false;
        }
    };

    const register = async (userData) => {
        setError(null);
        try {
            const response = await api.post('/api/v1/auth/register', userData);

            // После регистрации можно сразу войти или вернуть успех
            return { success: true, message: 'Регистрация успешна. Теперь вы можете войти.' };
        } catch (err) {
            console.error('Registration failed:', err);
            setError(err.response?.data?.message || 'Ошибка регистрации. Попробуйте другие данные.');
            return { success: false, message: err.response?.data?.message || 'Ошибка регистрации.' };
        }
    };

    const logout = () => {
        // Удаляем токен и сбрасываем состояние
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
        setCurrentUser(null);
        setIsAuthenticated(false);
    };

    const value = {
        currentUser,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 
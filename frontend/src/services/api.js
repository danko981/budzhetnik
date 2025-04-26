import axios from 'axios';

// Определяем базовый URL API в зависимости от окружения
const getBaseURL = () => {
    if (process.env.NODE_ENV === 'development') {
        // В режиме разработки фронтенд на порту 3000, бэкенд на 8000
        return 'http://localhost:8000';
    }
    // В продакшене API находится на том же домене, что и фронтенд
    return '';
};

// Создаем экземпляр axios с настройками по умолчанию
export const api = axios.create({
    baseURL: getBaseURL(), // Базовый URL - прокси настроен в Vite
    headers: {
        'Content-Type': 'application/json',
    },
});

// Перехватчик для добавления токена к запросам
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Перехватчик для обработки ответов
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Если ошибка 401 (неавторизованный) и не endpoint авторизации
        if (error.response && error.response.status === 401 &&
            !error.config.url.includes('/auth/login')) {
            // Можно вызвать logout или перенаправить на страницу логина
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API для работы с транзакциями
export const transactionsAPI = {
    getAll: async (params = {}) => {
        return api.get('/api/v1/transactions', { params });
    },
    getById: async (id) => {
        return api.get(`/api/v1/transactions/${id}`);
    },
    create: async (data) => {
        return api.post('/api/v1/transactions', data);
    },
    update: async (id, data) => {
        return api.put(`/api/v1/transactions/${id}`, data);
    },
    delete: async (id) => {
        return api.delete(`/api/v1/transactions/${id}`);
    }
};

// API для работы с категориями
export const categoriesAPI = {
    getAll: async (params = {}) => {
        return api.get('/api/v1/categories', { params });
    },
    getById: async (id) => {
        return api.get(`/api/v1/categories/${id}`);
    },
    create: async (data) => {
        return api.post('/api/v1/categories', data);
    },
    update: async (id, data) => {
        return api.put(`/api/v1/categories/${id}`, data);
    },
    delete: async (id) => {
        return api.delete(`/api/v1/categories/${id}`);
    }
};

// API для работы с бюджетами
export const budgetsAPI = {
    getAll: async (params = {}) => {
        return api.get('/api/v1/budgets', { params });
    },
    getById: async (id) => {
        return api.get(`/api/v1/budgets/${id}`);
    },
    create: async (data) => {
        return api.post('/api/v1/budgets', data);
    },
    update: async (id, data) => {
        return api.put(`/api/v1/budgets/${id}`, data);
    },
    delete: async (id) => {
        return api.delete(`/api/v1/budgets/${id}`);
    }
};

// API для отчетов
export const reportsAPI = {
    getIncomeExpenseSummary: async (params) => {
        return api.get('/api/v1/reports/income-expense', { params });
    },
    getCategorySummary: async (params) => {
        return api.get('/api/v1/reports/by-category', { params });
    },
    getBudgetPerformance: async (params) => {
        return api.get('/api/v1/reports/budget-performance', { params });
    }
};

// API для калькулятора
export const calculatorAPI = {
    calculateSavingsGoal: async (data) => {
        return api.post('/api/v1/calculator/savings-goal', data);
    }
};

// API для поддержки
export const supportAPI = {
    getFAQ: async () => {
        return api.get('/api/v1/support/faq');
    },
    getFAQItem: async (id) => {
        return api.get(`/api/v1/support/faq/${id}`);
    },
    sendContactForm: async (data) => {
        return api.post('/api/v1/support/contact', data);
    }
}; 
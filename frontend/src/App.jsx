import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';

// Импорт основных компонентов
import Layout from './components/Layout/Layout';

// Импорт страниц аутентификации
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';

// Импорт защищенных страниц
import Dashboard from './pages/Dashboard/Dashboard';
import Calculator from './pages/Calculator/Calculator';
import Transactions from './pages/Transactions/Transactions';
import Categories from './pages/Categories/Categories';
import Budgets from './pages/Budgets/Budgets';
import Reports from './pages/Reports/Reports';
import Profile from './pages/Profile/Profile';
import Settings from './pages/Settings/Settings';

// Импорт вспомогательных страниц
import NotFound from './pages/NotFound/NotFound';

// Настраиваем обработчик глобальных ошибок
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Ошибка в приложении:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    padding: '30px',
                    textAlign: 'center',
                    color: '#d32f2f',
                    fontFamily: 'Roboto, sans-serif'
                }}>
                    <h1>Что-то пошло не так.</h1>
                    <p>Попробуйте обновить страницу.</p>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            padding: '10px 20px',
                            background: '#2E7D32',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        Обновить страницу
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

// Функция для проверки авторизации
const RequireAuth = ({ children }) => {
    const isAuthenticated = localStorage.getItem('access_token') !== null || localStorage.getItem('token') !== null;
    return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
    return (
        <ErrorBoundary>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <HashRouter>
                    <Routes>
                        {/* Публичные маршруты */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />

                        {/* Защищенные маршруты */}
                        <Route
                            path="/"
                            element={
                                <RequireAuth>
                                    <Layout />
                                </RequireAuth>
                            }
                        >
                            <Route index element={<Dashboard />} />
                            <Route path="transactions" element={<Transactions />} />
                            <Route path="categories" element={<Categories />} />
                            <Route path="budgets" element={<Budgets />} />
                            <Route path="reports" element={<Reports />} />
                            <Route path="calculator" element={<Calculator />} />
                            <Route path="profile" element={<Profile />} />
                            <Route path="settings" element={<Settings />} />
                        </Route>

                        {/* Страница 404 */}
                        <Route path="*" element={<NotFound />} />
                    </Routes>
                </HashRouter>
            </ThemeProvider>
        </ErrorBoundary>
    );
}

export default App; 
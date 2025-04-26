import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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

// Функция для проверки авторизации
const RequireAuth = ({ children }) => {
    const isAuthenticated = localStorage.getItem('token') !== null;
    return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
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
            </BrowserRouter>
        </ThemeProvider>
    );
}

export default App; 
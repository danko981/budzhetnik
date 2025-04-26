import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, Container, Link, Alert } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Register = () => {
    const { register, error, testUsers } = useAuth();
    const navigate = useNavigate();

    // Состояния для формы
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [registerError, setRegisterError] = useState('');
    const [success, setSuccess] = useState('');

    // Валидация email
    const validateEmail = (email) => {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    };

    // Обработчик отправки формы
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Сбрасываем ошибки и успешные сообщения
        setRegisterError('');
        setSuccess('');

        // Проверка заполнения полей
        if (!username.trim() || !email.trim() || !password || !confirmPassword) {
            setRegisterError('Пожалуйста, заполните все поля');
            return;
        }

        // Проверка валидности email
        if (!validateEmail(email)) {
            setRegisterError('Пожалуйста, введите корректный email');
            return;
        }

        // Проверка длины пароля
        if (password.length < 6) {
            setRegisterError('Пароль должен содержать минимум 6 символов');
            return;
        }

        // Проверка совпадения паролей
        if (password !== confirmPassword) {
            setRegisterError('Пароли не совпадают');
            return;
        }

        // Проверка на конфликт с тестовыми учетными данными
        if (testUsers && testUsers.some(user => user.username === username)) {
            setRegisterError('Пользователь с таким именем уже существует');
            return;
        }

        setIsLoading(true);

        try {
            const result = await register({
                username,
                email,
                password
            });

            if (result.success) {
                setSuccess(result.message || 'Регистрация успешна. Теперь вы можете войти.');
                // Очищаем форму
                setUsername('');
                setEmail('');
                setPassword('');
                setConfirmPassword('');

                // Перенаправляем на страницу входа через 2 секунды
                setTimeout(() => {
                    navigate('/login');
                }, 2000);
            } else {
                setRegisterError(result.message || 'Ошибка при регистрации');
            }
        } catch (err) {
            console.error('Registration error:', err);
            setRegisterError('Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ p: 3, mt: 8 }}>
                <Typography variant="h4" component="h1" align="center" gutterBottom>
                    Регистрация
                </Typography>
                <Paper sx={{ p: 3 }}>
                    {registerError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {registerError}
                        </Alert>
                    )}
                    {success && (
                        <Alert severity="success" sx={{ mb: 2 }}>
                            {success}
                        </Alert>
                    )}
                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="username"
                            label="Имя пользователя"
                            name="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            autoFocus
                            disabled={isLoading}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email"
                            name="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isLoading}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Пароль"
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isLoading}
                            helperText="Минимум 6 символов"
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="confirmPassword"
                            label="Подтвердите пароль"
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            disabled={isLoading}
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2 }}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
                        </Button>
                        <Box textAlign="center">
                            <Link component={RouterLink} to="/login" variant="body2">
                                Уже есть аккаунт? Войти
                            </Link>
                        </Box>

                        {process.env.NODE_ENV === 'development' && (
                            <Box mt={3} p={2} bgcolor="grey.100" borderRadius={1}>
                                <Typography variant="caption" color="textSecondary">
                                    Тестовые учетные данные: demo/demo123, test/test123
                                </Typography>
                            </Box>
                        )}
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Register; 
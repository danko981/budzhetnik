import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, Container, Link, Alert } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Register = () => {
    const { register, error } = useAuth();
    const navigate = useNavigate();

    // Состояния для формы
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [registerError, setRegisterError] = useState('');

    // Обработчик отправки формы
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Проверка заполнения полей
        if (!username.trim() || !email.trim() || !password || !confirmPassword) {
            setRegisterError('Пожалуйста, заполните все поля');
            return;
        }

        // Проверка совпадения паролей
        if (password !== confirmPassword) {
            setRegisterError('Пароли не совпадают');
            return;
        }

        setIsLoading(true);
        setRegisterError('');

        try {
            const result = await register({
                username,
                email,
                password
            });

            if (result.success) {
                navigate('/login');
            } else {
                setRegisterError(result.message || 'Ошибка при регистрации');
            }
        } catch (err) {
            setRegisterError('Произошла ошибка при регистрации');
            console.error('Registration error:', err);
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
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
};

export default Register; 
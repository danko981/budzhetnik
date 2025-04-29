import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
    Avatar,
    Button,
    TextField,
    Link,
    Paper,
    Box,
    Grid,
    Typography,
    Alert,
    InputAdornment,
    IconButton,
    Container,
    Divider,
    Chip,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

const Login = () => {
    const { login, error, isAuthenticated, loading, testUsers } = useAuth();
    const { theme } = useTheme();
    const navigate = useNavigate();

    // Состояния для формы
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [loginError, setLoginError] = useState('');

    // Перенаправление, если пользователь уже аутентифицирован
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/');
        }
    }, [isAuthenticated, navigate]);

    // Обработчик отправки формы
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Сбрасываем ошибки
        setLoginError('');

        // Проверка на пустые поля
        if (!username.trim() || !password) {
            setLoginError('Пожалуйста, заполните все поля');
            return;
        }

        setIsLoading(true);

        try {
            const result = await login({ username, password });

            if (!result.success) {
                setLoginError(result.message || 'Не удалось войти в систему');
            }
            // Если успешно, useEffect перенаправит на главную
        } catch (err) {
            setLoginError('Произошла непредвиденная ошибка');
            console.error('Login error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Переключатель видимости пароля
    const handleTogglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    // Быстрый вход тестовым пользователем
    const loginAsTestUser = async (testUser) => {
        setUsername(testUser.username);
        setPassword(testUser.password);

        // Автоматический вход после выбора тестового пользователя
        setIsLoading(true);
        try {
            const result = await login({
                username: testUser.username,
                password: testUser.password
            });

            if (!result.success) {
                setLoginError(result.message || 'Не удалось войти тестовым пользователем');
            }
        } catch (err) {
            setLoginError('Произошла ошибка при входе тестовым пользователем');
            console.error('Test login error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    if (loading) {
        return (
            <Container maxWidth="sm">
                <Box sx={{ p: 3, mt: 8, textAlign: 'center' }}>
                    <Typography>Загрузка...</Typography>
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="sm">
            <Box sx={{ p: 3, mt: 8 }}>
                <Typography variant="h4" component="h1" align="center" gutterBottom>
                    Вход в систему
                </Typography>
                <Paper sx={{ p: 3 }}>
                    {loginError && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {loginError}
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
                            name="password"
                            label="Пароль"
                            type={showPassword ? "text" : "password"}
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isLoading}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle password visibility"
                                            onClick={handleTogglePasswordVisibility}
                                            edge="end"
                                        >
                                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2 }}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Вход...' : 'Войти'}
                        </Button>
                        <Box textAlign="center">
                            <Link component={RouterLink} to="/register" variant="body2">
                                Нет аккаунта? Зарегистрироваться
                            </Link>
                        </Box>
                    </Box>

                    {process.env.NODE_ENV === 'development' && (
                        <>
                            <Divider sx={{ my: 3 }}>
                                <Chip label="Тестовые пользователи" />
                            </Divider>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                {testUsers.map((user, index) => (
                                    <Button
                                        key={index}
                                        variant="outlined"
                                        size="small"
                                        onClick={() => loginAsTestUser(user)}
                                        sx={{ justifyContent: 'flex-start' }}
                                    >
                                        {user.username} / {user.password}
                                    </Button>
                                ))}
                            </Box>
                        </>
                    )}
                </Paper>
            </Box>
        </Container>
    );
};

export default Login; 
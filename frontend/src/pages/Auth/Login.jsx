import React, { useState } from 'react';
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
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';

const Login = () => {
    const { login, error } = useAuth();
    const { theme } = useTheme();
    const navigate = useNavigate();

    // Состояния для формы
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [loginError, setLoginError] = useState('');

    // Обработчик отправки формы
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!username.trim() || !password) {
            setLoginError('Пожалуйста, заполните все поля');
            return;
        }

        setIsLoading(true);
        setLoginError('');

        try {
            const success = await login({ username, password });
            if (success) {
                navigate('/');
            } else {
                setLoginError(error || 'Неверное имя пользователя или пароль');
            }
        } catch (err) {
            setLoginError('Произошла ошибка при входе в систему');
            console.error('Login error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTogglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

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
                </Paper>
            </Box>
        </Container>
    );
};

export default Login; 
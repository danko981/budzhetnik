import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    Typography,
    IconButton,
    Avatar,
    Box,
    Menu,
    MenuItem,
    Tooltip,
    Button,
    useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { useAuth } from '../../context/AuthContext';
import { useTheme as useAppTheme } from '../../context/ThemeContext';

const Header = ({ onDrawerToggle }) => {
    const { currentUser, logout } = useAuth();
    const { mode, toggleTheme } = useAppTheme();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    // Состояние для меню профиля
    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);

    // Обработчики для меню профиля
    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleLogout = () => {
        handleClose();
        logout();
    };

    return (
        <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
            <Toolbar>
                {/* Кнопка меню для мобильных устройств */}
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    edge="start"
                    onClick={onDrawerToggle}
                    sx={{ mr: 2, display: { sm: 'none' } }}
                >
                    <MenuIcon />
                </IconButton>

                {/* Логотип */}
                <Typography
                    variant="h6"
                    component={RouterLink}
                    to="/"
                    sx={{
                        flexGrow: 1,
                        textDecoration: 'none',
                        color: 'inherit',
                        display: 'flex',
                        alignItems: 'center',
                    }}
                >
                    Budgetnik
                </Typography>

                {/* Кнопка переключения темы */}
                <Tooltip title={mode === 'light' ? 'Тёмная тема' : 'Светлая тема'}>
                    <IconButton color="inherit" onClick={toggleTheme} sx={{ mr: 1 }}>
                        {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
                    </IconButton>
                </Tooltip>

                {/* Профиль пользователя */}
                <Box>
                    <Tooltip title="Профиль">
                        <IconButton
                            onClick={handleClick}
                            size="small"
                            aria-controls={open ? 'account-menu' : undefined}
                            aria-haspopup="true"
                            aria-expanded={open ? 'true' : undefined}
                            aria-label="account of current user"
                            color="inherit"
                        >
                            {currentUser?.username ? (
                                <Avatar
                                    alt={currentUser.username}
                                    src={currentUser.avatar}
                                    sx={{ width: 32, height: 32 }}
                                >
                                    {currentUser.username.charAt(0).toUpperCase()}
                                </Avatar>
                            ) : (
                                <AccountCircleIcon />
                            )}
                        </IconButton>
                    </Tooltip>
                </Box>

                {/* Меню профиля */}
                <Menu
                    id="account-menu"
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                    transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                    anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                >
                    <MenuItem component={RouterLink} to="/profile" onClick={handleClose}>
                        Профиль
                    </MenuItem>
                    <MenuItem component={RouterLink} to="/settings" onClick={handleClose}>
                        Настройки
                    </MenuItem>
                    <MenuItem onClick={handleLogout}>Выйти</MenuItem>
                </Menu>
            </Toolbar>
        </AppBar>
    );
};

export default Header; 
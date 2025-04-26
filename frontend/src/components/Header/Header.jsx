import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    IconButton,
    Typography,
    Box,
    Badge,
    Menu,
    MenuItem,
    InputBase,
    Avatar,
    Tooltip,
    Divider,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import {
    Menu as MenuIcon,
    Notifications as NotificationsIcon,
    Search as SearchIcon,
    AccountCircle,
    Logout,
    Settings,
    Person,
} from '@mui/icons-material';

// Стилизованные компоненты для поиска
const Search = styled('div')(({ theme }) => ({
    position: 'relative',
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.common.white, 0.15),
    '&:hover': {
        backgroundColor: alpha(theme.palette.common.white, 0.25),
    },
    marginRight: theme.spacing(2),
    marginLeft: 0,
    width: '100%',
    [theme.breakpoints.up('sm')]: {
        marginLeft: theme.spacing(3),
        width: 'auto',
    },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
    padding: theme.spacing(0, 2),
    height: '100%',
    position: 'absolute',
    pointerEvents: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
    color: 'inherit',
    '& .MuiInputBase-input': {
        padding: theme.spacing(1, 1, 1, 0),
        paddingLeft: `calc(1em + ${theme.spacing(4)})`,
        transition: theme.transitions.create('width'),
        width: '100%',
        [theme.breakpoints.up('md')]: {
            width: '20ch',
        },
    },
}));

const Header = ({ onToggleSidebar, sidebarOpen }) => {
    const navigate = useNavigate();
    const [searchValue, setSearchValue] = useState('');

    // Состояния для меню
    const [anchorElUser, setAnchorElUser] = useState(null);
    const [anchorElNotifications, setAnchorElNotifications] = useState(null);

    // Обработчики для меню пользователя
    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    // Обработчики для меню уведомлений
    const handleOpenNotificationsMenu = (event) => {
        setAnchorElNotifications(event.currentTarget);
    };

    const handleCloseNotificationsMenu = () => {
        setAnchorElNotifications(null);
    };

    // Обработчик поиска
    const handleSearchChange = (e) => {
        setSearchValue(e.target.value);
    };

    // Обработчик выхода из системы
    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <AppBar
            position="sticky"
            sx={{
                zIndex: (theme) => theme.zIndex.drawer + 1,
                boxShadow: 1,
            }}
        >
            <Toolbar>
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    edge="start"
                    onClick={onToggleSidebar}
                    sx={{ mr: 2 }}
                >
                    <MenuIcon />
                </IconButton>

                <Typography
                    variant="h6"
                    noWrap
                    component="div"
                    sx={{ display: { xs: 'none', sm: 'block' } }}
                >
                    Бюджетник
                </Typography>

                <Search>
                    <SearchIconWrapper>
                        <SearchIcon />
                    </SearchIconWrapper>
                    <StyledInputBase
                        placeholder="Поиск..."
                        inputProps={{ 'aria-label': 'search' }}
                        value={searchValue}
                        onChange={handleSearchChange}
                    />
                </Search>

                <Box sx={{ flexGrow: 1 }} />

                {/* Уведомления */}
                <Box sx={{ display: 'flex' }}>
                    <IconButton
                        size="large"
                        color="inherit"
                        onClick={handleOpenNotificationsMenu}
                    >
                        <Badge badgeContent={4} color="error">
                            <NotificationsIcon />
                        </Badge>
                    </IconButton>
                    <Menu
                        id="notifications-menu"
                        anchorEl={anchorElNotifications}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'right',
                        }}
                        keepMounted
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                        open={Boolean(anchorElNotifications)}
                        onClose={handleCloseNotificationsMenu}
                        sx={{ mt: '45px' }}
                    >
                        <MenuItem onClick={handleCloseNotificationsMenu}>
                            <Typography variant="body2">Вы превысили лимит бюджета</Typography>
                        </MenuItem>
                        <MenuItem onClick={handleCloseNotificationsMenu}>
                            <Typography variant="body2">Новое обновление доступно</Typography>
                        </MenuItem>
                        <MenuItem onClick={handleCloseNotificationsMenu}>
                            <Typography variant="body2">Напоминание о регулярном платеже</Typography>
                        </MenuItem>
                        <Divider />
                        <MenuItem onClick={handleCloseNotificationsMenu}>
                            <Typography variant="body2" color="primary">Просмотреть все уведомления</Typography>
                        </MenuItem>
                    </Menu>

                    {/* Пользовательское меню */}
                    <Tooltip title="Аккаунт">
                        <IconButton
                            onClick={handleOpenUserMenu}
                            sx={{ p: 0, ml: 2 }}
                            color="inherit"
                        >
                            <Avatar alt="User" />
                        </IconButton>
                    </Tooltip>
                    <Menu
                        id="menu-appbar"
                        anchorEl={anchorElUser}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'right',
                        }}
                        keepMounted
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                        open={Boolean(anchorElUser)}
                        onClose={handleCloseUserMenu}
                        sx={{ mt: '45px' }}
                    >
                        <MenuItem onClick={() => { handleCloseUserMenu(); navigate('/profile'); }}>
                            <Person sx={{ mr: 1 }} />
                            <Typography textAlign="center">Профиль</Typography>
                        </MenuItem>
                        <MenuItem onClick={() => { handleCloseUserMenu(); navigate('/settings'); }}>
                            <Settings sx={{ mr: 1 }} />
                            <Typography textAlign="center">Настройки</Typography>
                        </MenuItem>
                        <Divider />
                        <MenuItem onClick={handleLogout}>
                            <Logout sx={{ mr: 1 }} />
                            <Typography textAlign="center">Выход</Typography>
                        </MenuItem>
                    </Menu>
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Header; 
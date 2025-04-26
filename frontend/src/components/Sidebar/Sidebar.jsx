import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    Box,
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Divider,
    Toolbar,
    Typography,
    useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
    Dashboard as DashboardIcon,
    Receipt as ReceiptIcon,
    Category as CategoryIcon,
    AccountBalance as AccountBalanceIcon,
    BarChart as BarChartIcon,
    Calculate as CalculateIcon,
    Settings as SettingsIcon,
    Help as HelpIcon,
    Person as PersonIcon,
} from '@mui/icons-material';

// Ширина боковой панели
const drawerWidth = 240;

// Навигационные пункты меню
const menuItems = [
    {
        title: 'Главная',
        path: '/',
        icon: <DashboardIcon />,
    },
    {
        title: 'Транзакции',
        path: '/transactions',
        icon: <ReceiptIcon />,
    },
    {
        title: 'Категории',
        path: '/categories',
        icon: <CategoryIcon />,
    },
    {
        title: 'Бюджеты',
        path: '/budgets',
        icon: <AccountBalanceIcon />,
    },
    {
        title: 'Отчеты',
        path: '/reports',
        icon: <BarChartIcon />,
    },
    {
        title: 'Калькулятор',
        path: '/calculator',
        icon: <CalculateIcon />,
    },
];

// Служебные пункты меню
const utilityItems = [
    {
        title: 'Профиль',
        path: '/profile',
        icon: <PersonIcon />,
    },
    {
        title: 'Настройки',
        path: '/settings',
        icon: <SettingsIcon />,
    },
];

const Sidebar = ({ open, onClose }) => {
    const theme = useTheme();
    const location = useLocation();
    const navigate = useNavigate();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));

    // Содержимое меню
    const drawerContent = (
        <>
            <Toolbar sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderBottom: `1px solid ${theme.palette.divider}`,
                minHeight: '64px', // Фиксированная высота для устранения скачков
            }}>
                <Typography variant="h6" component="div" color="primary" fontWeight="bold">
                    Бюджетник
                </Typography>
            </Toolbar>

            <Box sx={{ overflow: 'auto', mt: 1, px: 1 }}>
                <List disablePadding>
                    {menuItems.map((item) => (
                        <ListItem key={item.title} disablePadding sx={{ mb: 0.5 }}>
                            <ListItemButton
                                selected={location.pathname === item.path}
                                onClick={() => {
                                    navigate(item.path);
                                    if (isMobile) onClose();
                                }}
                                sx={{
                                    borderRadius: '8px',
                                    height: '48px',
                                    '&.Mui-selected': {
                                        bgcolor: 'primary.light',
                                        color: 'primary.contrastText',
                                        '& .MuiListItemIcon-root': {
                                            color: 'primary.contrastText',
                                        },
                                    },
                                    '&:hover': {
                                        bgcolor: theme.palette.mode === 'dark'
                                            ? 'rgba(255, 255, 255, 0.08)'
                                            : 'rgba(0, 0, 0, 0.04)',
                                    },
                                }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 40,
                                        color: location.pathname === item.path ? 'primary.contrastText' : 'inherit',
                                    }}
                                >
                                    {item.icon}
                                </ListItemIcon>
                                <ListItemText primary={item.title} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>

                <Divider sx={{ my: 1 }} />

                <List disablePadding>
                    {utilityItems.map((item) => (
                        <ListItem key={item.title} disablePadding sx={{ mb: 0.5 }}>
                            <ListItemButton
                                selected={location.pathname === item.path}
                                onClick={() => {
                                    navigate(item.path);
                                    if (isMobile) onClose();
                                }}
                                sx={{
                                    borderRadius: '8px',
                                    height: '48px',
                                    '&.Mui-selected': {
                                        bgcolor: 'primary.light',
                                        color: 'primary.contrastText',
                                        '& .MuiListItemIcon-root': {
                                            color: 'primary.contrastText',
                                        },
                                    },
                                    '&:hover': {
                                        bgcolor: theme.palette.mode === 'dark'
                                            ? 'rgba(255, 255, 255, 0.08)'
                                            : 'rgba(0, 0, 0, 0.04)',
                                    },
                                }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 40,
                                        color: location.pathname === item.path ? 'primary.contrastText' : 'inherit',
                                    }}
                                >
                                    {item.icon}
                                </ListItemIcon>
                                <ListItemText primary={item.title} />
                            </ListItemButton>
                        </ListItem>
                    ))}
                </List>
            </Box>
        </>
    );

    return (
        <Box
            component="nav"
            sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        >
            {/* Мобильная версия */}
            {isMobile ? (
                <Drawer
                    variant="temporary"
                    open={open}
                    onClose={onClose}
                    ModalProps={{
                        keepMounted: true, // Улучшает производительность на мобильных устройствах
                    }}
                    sx={{
                        display: { xs: 'block', md: 'none' },
                        '& .MuiDrawer-paper': {
                            boxSizing: 'border-box',
                            width: drawerWidth,
                            overflowX: 'hidden',
                            transition: theme.transitions.create('width', {
                                easing: theme.transitions.easing.sharp,
                                duration: theme.transitions.duration.enteringScreen,
                            }),
                        },
                    }}
                >
                    {drawerContent}
                </Drawer>
            ) : (
                // Десктопная версия
                <Drawer
                    variant="persistent"
                    open={open}
                    sx={{
                        display: { xs: 'none', md: 'block' },
                        '& .MuiDrawer-paper': {
                            boxSizing: 'border-box',
                            width: drawerWidth,
                            borderRight: `1px solid ${theme.palette.divider}`,
                            overflowX: 'hidden',
                            transition: theme.transitions.create(['width', 'box-shadow'], {
                                easing: theme.transitions.easing.easeOut,
                                duration: theme.transitions.duration.enteringScreen,
                            }),
                            boxShadow: open ? '0px 2px 4px -1px rgba(0,0,0,0.1), 0px 4px 5px 0px rgba(0,0,0,0.07), 0px 1px 10px 0px rgba(0,0,0,0.06)' : 'none',
                        },
                    }}
                >
                    {drawerContent}
                </Drawer>
            )}
        </Box>
    );
};

export default Sidebar; 
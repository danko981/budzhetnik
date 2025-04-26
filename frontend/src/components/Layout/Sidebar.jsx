import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ListItemButton,
    Divider,
    Toolbar,
    Box,
    useTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import CategoryIcon from '@mui/icons-material/Category';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import BarChartIcon from '@mui/icons-material/BarChart';
import CalculateIcon from '@mui/icons-material/Calculate';
import HelpIcon from '@mui/icons-material/Help';

// Ширина боковой панели
const drawerWidth = 240;

// Элементы меню
const menuItems = [
    { text: 'Дашборд', path: '/', icon: <DashboardIcon /> },
    { text: 'Транзакции', path: '/transactions', icon: <MonetizationOnIcon /> },
    { text: 'Категории', path: '/categories', icon: <CategoryIcon /> },
    { text: 'Бюджеты', path: '/budgets', icon: <AccountBalanceWalletIcon /> },
    { text: 'Отчеты', path: '/reports', icon: <BarChartIcon /> },
    { text: 'Калькулятор', path: '/calculator', icon: <CalculateIcon /> },
];

// Вспомогательные пункты меню
const secondaryMenuItems = [
    { text: 'Поддержка', path: '/support', icon: <HelpIcon /> },
];

const Sidebar = ({ mobileOpen, onClose }) => {
    const location = useLocation();
    const navigate = useNavigate();
    const theme = useTheme();

    // Содержимое панели
    const drawer = (
        <div>
            <Toolbar />
            <Divider />
            <List>
                {menuItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            selected={location.pathname === item.path}
                            onClick={() => {
                                navigate(item.path);
                                if (mobileOpen) onClose();
                            }}
                            sx={{
                                '&.Mui-selected': {
                                    backgroundColor: theme.palette.action.selected,
                                    borderRight: `3px solid ${theme.palette.primary.main}`,
                                    '&:hover': {
                                        backgroundColor: theme.palette.action.hover,
                                    },
                                },
                            }}
                        >
                            <ListItemIcon
                                sx={{
                                    color: location.pathname === item.path
                                        ? theme.palette.primary.main
                                        : 'inherit',
                                }}
                            >
                                {item.icon}
                            </ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                {secondaryMenuItems.map((item) => (
                    <ListItem key={item.text} disablePadding>
                        <ListItemButton
                            selected={location.pathname === item.path}
                            onClick={() => {
                                navigate(item.path);
                                if (mobileOpen) onClose();
                            }}
                        >
                            <ListItemIcon>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </div>
    );

    return (
        <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            aria-label="основное меню"
        >
            {/* Мобильная версия (временно появляющееся меню) */}
            <Drawer
                variant="temporary"
                open={mobileOpen}
                onClose={onClose}
                ModalProps={{ keepMounted: true }}
                sx={{
                    display: { xs: 'block', sm: 'none' },
                    '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
            >
                {drawer}
            </Drawer>

            {/* Десктопная версия (постоянное меню) */}
            <Drawer
                variant="permanent"
                sx={{
                    display: { xs: 'none', sm: 'block' },
                    '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                }}
                open
            >
                {drawer}
            </Drawer>
        </Box>
    );
};

export default Sidebar; 
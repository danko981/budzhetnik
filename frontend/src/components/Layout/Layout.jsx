import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Toolbar, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Header from './Header';
import Sidebar from './Sidebar';

// Ширина боковой панели (должна совпадать с Sidebar.jsx)
const drawerWidth = 200;

const Layout = () => {
    const [mobileOpen, setMobileOpen] = useState(false);
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Заголовок */}
            <Header onDrawerToggle={handleDrawerToggle} />

            {/* Боковая панель */}
            <Sidebar mobileOpen={mobileOpen} onClose={handleDrawerToggle} />

            {/* Основное содержимое */}
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    width: { xs: '100%', sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { xs: 0, sm: `${drawerWidth}px` },
                    p: { xs: 2, sm: 3 },
                    backgroundColor: theme.palette.background.default,
                }}
            >
                <Toolbar /> {/* Отступ для заголовка */}
                <Outlet />
            </Box>
        </Box>
    );
};

export default Layout; 
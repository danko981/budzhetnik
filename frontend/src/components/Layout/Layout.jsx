import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box, useMediaQuery, CssBaseline } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Sidebar from '../Sidebar/Sidebar';
import Header from '../Header/Header';

const Layout = () => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('md'));
    const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

    const handleToggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <CssBaseline />
            <Sidebar open={sidebarOpen} onClose={handleToggleSidebar} />

            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: '100vh',
                    width: { xs: '100%', md: `calc(100% - ${sidebarOpen ? 240 : 0}px)` },
                    transition: theme.transitions.create(['margin', 'width'], {
                        easing: theme.transitions.easing.easeOut,
                        duration: theme.transitions.duration.enteringScreen,
                    }),
                    ml: { xs: 0, md: sidebarOpen ? '240px' : 0 },
                }}
            >
                <Header onToggleSidebar={handleToggleSidebar} sidebarOpen={sidebarOpen} />

                <Box
                    sx={{
                        flexGrow: 1,
                        p: 3,
                        bgcolor: theme.palette.background.default,
                        overflow: 'auto',
                        transition: theme.transitions.create('padding', {
                            easing: theme.transitions.easing.easeOut,
                            duration: theme.transitions.duration.enteringScreen,
                        }),
                    }}
                >
                    <Outlet />
                </Box>
            </Box>
        </Box>
    );
};

export default Layout; 
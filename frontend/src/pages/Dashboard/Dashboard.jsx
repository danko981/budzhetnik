import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Dashboard = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Главная страница
            </Typography>
            <Paper sx={{ p: 3 }}>
                <Typography>
                    Добро пожаловать в приложение для управления личным бюджетом.
                </Typography>
            </Paper>
        </Box>
    );
};

export default Dashboard; 
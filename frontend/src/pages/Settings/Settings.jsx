import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Settings = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Настройки
            </Typography>
            <Paper sx={{ p: 3 }}>
                <Typography>
                    Здесь будут отображаться настройки приложения.
                </Typography>
            </Paper>
        </Box>
    );
};

export default Settings; 
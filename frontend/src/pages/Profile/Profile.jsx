import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Profile = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Профиль
            </Typography>
            <Paper sx={{ p: 3 }}>
                <Typography>
                    Здесь будет отображаться информация о вашем профиле.
                </Typography>
            </Paper>
        </Box>
    );
};

export default Profile; 
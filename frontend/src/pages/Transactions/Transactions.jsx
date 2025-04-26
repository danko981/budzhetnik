import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Transactions = () => {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Транзакции
            </Typography>
            <Paper sx={{ p: 3 }}>
                <Typography>
                    Здесь будет отображаться список ваших транзакций.
                </Typography>
            </Paper>
        </Box>
    );
};

export default Transactions; 
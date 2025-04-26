import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Button, Typography, Container } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import HomeIcon from '@mui/icons-material/Home';

const NotFound = () => {
    return (
        <Container
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
                textAlign: 'center'
            }}
        >
            <ErrorOutlineIcon sx={{ fontSize: 100, color: 'error.main', mb: 2 }} />

            <Typography variant="h1" sx={{ fontSize: { xs: '4rem', md: '6rem' }, fontWeight: 700, mb: 2 }}>
                404
            </Typography>

            <Typography variant="h4" sx={{ mb: 2 }}>
                Страница не найдена
            </Typography>

            <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600 }}>
                Извините, мы не смогли найти запрашиваемую страницу. Возможно, она была перемещена, удалена или никогда не существовала.
            </Typography>

            <Button
                variant="contained"
                color="primary"
                component={RouterLink}
                to="/"
                startIcon={<HomeIcon />}
                size="large"
            >
                Вернуться на главную
            </Button>
        </Container>
    );
};

export default NotFound; 
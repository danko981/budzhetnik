import React, { useState } from 'react';
import { format, addMonths } from 'date-fns';
import { ru } from 'date-fns/locale';
import {
    Box,
    Typography,
    TextField,
    Button,
    Card,
    CardContent,
    Grid,
    Alert,
    CircularProgress,
    InputAdornment,
    List,
    ListItem,
    ListItemText,
    Divider,
    Paper,
    FormControl,
    FormHelperText,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CalculateIcon from '@mui/icons-material/Calculate';
import SavingsIcon from '@mui/icons-material/Savings';
import { calculatorAPI } from '../../services/api';

const Calculator = () => {
    // Состояния для формы
    const [targetAmount, setTargetAmount] = useState('');
    const [currentSavings, setCurrentSavings] = useState('0');
    const [targetDate, setTargetDate] = useState(addMonths(new Date(), 12)); // Через год по умолчанию

    // Состояния для результатов и UI
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Валидация формы
    const [formErrors, setFormErrors] = useState({
        targetAmount: '',
        targetDate: '',
        currentSavings: '',
    });

    const validateForm = () => {
        const errors = {
            targetAmount: '',
            targetDate: '',
            currentSavings: '',
        };
        let isValid = true;

        // Проверка целевой суммы
        if (!targetAmount || parseFloat(targetAmount) <= 0) {
            errors.targetAmount = 'Целевая сумма должна быть положительным числом';
            isValid = false;
        }

        // Проверка даты
        if (!targetDate) {
            errors.targetDate = 'Пожалуйста, выберите дату цели';
            isValid = false;
        } else if (targetDate <= new Date()) {
            errors.targetDate = 'Дата должна быть в будущем';
            isValid = false;
        }

        // Проверка текущих сбережений
        if (currentSavings && parseFloat(currentSavings) < 0) {
            errors.currentSavings = 'Текущие сбережения не могут быть отрицательными';
            isValid = false;
        }

        setFormErrors(errors);
        return isValid;
    };

    // Обработчик формы
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            const formattedDate = format(targetDate, 'yyyy-MM-dd');

            const response = await calculatorAPI.calculateSavingsGoal({
                target_amount: targetAmount,
                target_date: formattedDate,
                current_savings: currentSavings || '0',
            });

            setResult(response.data);
        } catch (err) {
            console.error('Error calculating savings goal:', err);
            setError(
                err.response?.data?.message ||
                'Произошла ошибка при расчете. Пожалуйста, проверьте введенные данные.'
            );
            setResult(null);
        } finally {
            setIsLoading(false);
        }
    };

    // Форматирование денежных сумм
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 2,
        }).format(amount);
    };

    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom>
                Калькулятор сбережений
            </Typography>

            <Typography variant="body1" color="text.secondary" paragraph>
                Рассчитайте, сколько нужно откладывать ежемесячно для достижения вашей финансовой цели.
            </Typography>

            <Grid container spacing={3} sx={{ mt: 1 }}>
                {/* Форма калькулятора */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Параметры расчета
                            </Typography>

                            <Box component="form" onSubmit={handleSubmit} noValidate>
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    id="targetAmount"
                                    label="Целевая сумма"
                                    name="targetAmount"
                                    value={targetAmount}
                                    onChange={(e) => setTargetAmount(e.target.value)}
                                    InputProps={{
                                        startAdornment: <InputAdornment position="start">₽</InputAdornment>,
                                    }}
                                    error={!!formErrors.targetAmount}
                                    helperText={formErrors.targetAmount}
                                    disabled={isLoading}
                                />

                                <TextField
                                    margin="normal"
                                    fullWidth
                                    id="currentSavings"
                                    label="Текущие накопления"
                                    name="currentSavings"
                                    value={currentSavings}
                                    onChange={(e) => setCurrentSavings(e.target.value)}
                                    InputProps={{
                                        startAdornment: <InputAdornment position="start">₽</InputAdornment>,
                                    }}
                                    error={!!formErrors.currentSavings}
                                    helperText={formErrors.currentSavings}
                                    disabled={isLoading}
                                />

                                <FormControl fullWidth margin="normal" error={!!formErrors.targetDate}>
                                    <DatePicker
                                        label="Дата достижения цели"
                                        value={targetDate}
                                        onChange={(newDate) => setTargetDate(newDate)}
                                        format="dd.MM.yyyy"
                                        disablePast
                                        slotProps={{
                                            textField: {
                                                fullWidth: true,
                                                required: true,
                                                error: !!formErrors.targetDate,
                                            },
                                        }}
                                        disabled={isLoading}
                                    />
                                    {formErrors.targetDate && (
                                        <FormHelperText>{formErrors.targetDate}</FormHelperText>
                                    )}
                                </FormControl>

                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="contained"
                                    color="primary"
                                    sx={{ mt: 3, mb: 2 }}
                                    startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <CalculateIcon />}
                                    disabled={isLoading}
                                >
                                    {isLoading ? 'Расчет...' : 'Рассчитать'}
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Результаты расчета */}
                <Grid item xs={12} md={6}>
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    {result && (
                        <Paper elevation={3} sx={{ p: 3 }}>
                            <Box display="flex" alignItems="center" mb={2}>
                                <SavingsIcon color="primary" fontSize="large" sx={{ mr: 1 }} />
                                <Typography variant="h6">Результаты расчета</Typography>
                            </Box>

                            <Divider sx={{ mb: 2 }} />

                            <List disablePadding>
                                <ListItem>
                                    <ListItemText
                                        primary="Целевая сумма"
                                        secondary={formatCurrency(parseFloat(result.target_amount))}
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemText
                                        primary="Текущие накопления"
                                        secondary={formatCurrency(parseFloat(result.current_savings))}
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemText
                                        primary="Осталось накопить"
                                        secondary={formatCurrency(parseFloat(result.amount_to_save))}
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemText
                                        primary="Срок"
                                        secondary={`${result.months_remaining} ${result.months_remaining === 1 ? 'месяц' :
                                            result.months_remaining >= 2 && result.months_remaining <= 4 ? 'месяца' :
                                                'месяцев'
                                            }`}
                                    />
                                </ListItem>
                                <Divider sx={{ my: 1 }} />
                                <ListItem sx={{ backgroundColor: (theme) => theme.palette.action.hover }}>
                                    <ListItemText
                                        primary={
                                            <Typography variant="subtitle1" fontWeight="bold">
                                                Ежемесячный платеж
                                            </Typography>
                                        }
                                        secondary={
                                            <Typography variant="h5" color="primary.main">
                                                {result.message ?
                                                    'Цель уже достигнута!' :
                                                    formatCurrency(parseFloat(result.required_monthly_savings))}
                                            </Typography>
                                        }
                                    />
                                </ListItem>
                                {result.message && (
                                    <ListItem>
                                        <ListItemText
                                            primary={<Typography color="success.main">{result.message}</Typography>}
                                        />
                                    </ListItem>
                                )}
                            </List>
                        </Paper>
                    )}

                    {!result && !error && (
                        <Box
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                height: '100%',
                                minHeight: 200,
                                p: 3,
                                backgroundColor: (theme) => theme.palette.background.paper,
                                borderRadius: 1
                            }}
                        >
                            <TrendingUpIcon color="disabled" sx={{ fontSize: 60, mb: 2 }} />
                            <Typography variant="body1" color="text.secondary" align="center">
                                Заполните форму слева и нажмите "Рассчитать", чтобы узнать необходимую сумму ежемесячных сбережений.
                            </Typography>
                        </Box>
                    )}
                </Grid>
            </Grid>
        </Box>
    );
};

export default Calculator; 
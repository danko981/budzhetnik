import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    TextField,
    Grid,
    Paper,
    Divider,
    Stack,
    Alert,
    InputAdornment,
    Card,
    CardContent,
    Slider,
    Button,
    Tooltip,
    IconButton,
    CircularProgress
} from '@mui/material';
import {
    Info as InfoIcon,
    AddCircleOutline as AddIcon,
    RemoveCircleOutline as RemoveIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

const BudgetCalculatorWidget = ({
    totalAmount,
    expenseCategories,
    expenseAllocations,
    onAllocationChange,
    startDate,
    endDate
}) => {
    // Состояния
    const [unallocatedAmount, setUnallocatedAmount] = useState(0);
    const [percentages, setPercentages] = useState({});
    const [isAutoAllocating, setIsAutoAllocating] = useState(false);

    // Обновление нераспределенной суммы при изменении входных данных
    useEffect(() => {
        calculateUnallocatedAmount();
    }, [totalAmount, expenseAllocations]);

    // Расчет нераспределенной суммы
    const calculateUnallocatedAmount = () => {
        const total = parseFloat(totalAmount) || 0;
        let allocated = 0;

        for (const categoryId in expenseAllocations) {
            allocated += parseFloat(expenseAllocations[categoryId] || 0);
        }

        setUnallocatedAmount(total - allocated);

        // Расчет процентов распределения для каждой категории
        const newPercentages = {};
        for (const categoryId in expenseAllocations) {
            const amount = parseFloat(expenseAllocations[categoryId] || 0);
            newPercentages[categoryId] = total > 0 ? (amount / total) * 100 : 0;
        }
        setPercentages(newPercentages);
    };

    // Форматирование денежных сумм
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(amount);
    };

    // Обработчик изменения распределения через слайдер
    const handleSliderChange = (categoryId, newPercentage) => {
        const total = parseFloat(totalAmount) || 0;
        const newAmount = (newPercentage * total) / 100;

        // Обновляем процент
        setPercentages({
            ...percentages,
            [categoryId]: newPercentage
        });

        // Вызываем callback для обновления суммы в родительском компоненте
        onAllocationChange(categoryId, newAmount.toFixed(0));
    };

    // Быстрые действия для увеличения/уменьшения суммы
    const adjustAllocation = (categoryId, adjustment) => {
        const currentValue = parseFloat(expenseAllocations[categoryId] || 0);
        const newValue = Math.max(0, currentValue + adjustment);
        onAllocationChange(categoryId, newValue.toFixed(0));
    };

    // Автоматическое распределение оставшейся суммы
    const autoAllocate = () => {
        setIsAutoAllocating(true);

        // Если нет категорий, ничего не делаем
        if (expenseCategories.length === 0) {
            setIsAutoAllocating(false);
            return;
        }

        setTimeout(() => {
            const total = parseFloat(totalAmount) || 0;

            if (total <= 0) {
                setIsAutoAllocating(false);
                return;
            }

            // Распределяем сумму поровну между всеми категориями
            const amountPerCategory = total / expenseCategories.length;

            const newAllocations = {};
            expenseCategories.forEach(category => {
                newAllocations[category.id] = amountPerCategory.toFixed(0);
            });

            // Обновляем все распределения сразу
            expenseCategories.forEach(category => {
                onAllocationChange(category.id, newAllocations[category.id]);
            });

            setIsAutoAllocating(false);
        }, 500); // Небольшая задержка для анимации
    };

    // Расчет дней между датами
    const calculateDays = () => {
        if (!startDate || !endDate) return 0;

        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    };

    // Расчет суммы в день
    const calculateDailyAmount = () => {
        const total = parseFloat(totalAmount) || 0;
        const days = calculateDays();

        if (days === 0) return 0;
        return total / days;
    };

    return (
        <Box>
            <Grid container spacing={3}>
                {/* Информация о бюджете */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 2, mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Калькулятор бюджета
                        </Typography>

                        <Grid container spacing={2}>
                            <Grid item xs={12} md={4}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="subtitle2" color="text.secondary">
                                            Общая сумма
                                        </Typography>
                                        <Typography variant="h5">
                                            {formatCurrency(parseFloat(totalAmount) || 0)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="subtitle2" color="text.secondary">
                                            Распределено
                                        </Typography>
                                        <Typography variant="h5">
                                            {formatCurrency((parseFloat(totalAmount) || 0) - unallocatedAmount)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="subtitle2" color="text.secondary">
                                            Остаток
                                        </Typography>
                                        <Typography
                                            variant="h5"
                                            color={unallocatedAmount < 0 ? 'error.main' : (unallocatedAmount > 0 ? 'success.main' : 'text.primary')}
                                        >
                                            {formatCurrency(unallocatedAmount)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>

                        <Box mt={2}>
                            {unallocatedAmount < 0 && (
                                <Alert severity="error" sx={{ mb: 2 }}>
                                    Превышение бюджета на {formatCurrency(Math.abs(unallocatedAmount))}
                                </Alert>
                            )}

                            {unallocatedAmount > 0 && parseFloat(totalAmount) > 0 && (
                                <Alert severity="info" sx={{ mb: 2 }}>
                                    У вас есть нераспределенная сумма {formatCurrency(unallocatedAmount)}
                                </Alert>
                            )}

                            <Button
                                variant="outlined"
                                startIcon={isAutoAllocating ? <CircularProgress size={20} /> : <TrendingUpIcon />}
                                onClick={autoAllocate}
                                disabled={isAutoAllocating || parseFloat(totalAmount) <= 0}
                                fullWidth
                            >
                                Автоматически распределить средства
                            </Button>
                        </Box>
                    </Paper>
                </Grid>

                {/* Дополнительные расчеты */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 2, mb: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>
                            Анализ бюджета
                        </Typography>
                        <Divider sx={{ mb: 2 }} />

                        <Grid container spacing={2}>
                            <Grid item xs={12} md={4}>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Период бюджета
                                    </Typography>
                                    <Typography variant="body1">
                                        {calculateDays()} дней
                                    </Typography>
                                </Box>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Сумма в день
                                    </Typography>
                                    <Typography variant="body1">
                                        {formatCurrency(calculateDailyAmount())}
                                    </Typography>
                                </Box>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Box>
                                    <Typography variant="body2" color="text.secondary">
                                        Сумма в месяц (в среднем)
                                    </Typography>
                                    <Typography variant="body1">
                                        {formatCurrency(calculateDailyAmount() * 30)}
                                    </Typography>
                                </Box>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>

                {/* Распределение по категориям */}
                <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                        Распределение по категориям
                    </Typography>

                    {expenseCategories.length === 0 ? (
                        <Alert severity="info">
                            Добавьте категории расходов, чтобы распределить бюджет
                        </Alert>
                    ) : (
                        <Stack spacing={2}>
                            {expenseCategories.map((category) => (
                                <Paper key={category.id} sx={{ p: 2 }}>
                                    <Grid container spacing={2} alignItems="center">
                                        <Grid item xs={12} sm={3}>
                                            <Box display="flex" alignItems="center">
                                                <Box
                                                    sx={{
                                                        width: 16,
                                                        height: 16,
                                                        borderRadius: '50%',
                                                        bgcolor: category.color || '#ccc',
                                                        mr: 1
                                                    }}
                                                />
                                                <Typography variant="body1">{category.name}</Typography>
                                            </Box>
                                        </Grid>

                                        <Grid item xs={12} sm={6}>
                                            <Slider
                                                value={percentages[category.id] || 0}
                                                onChange={(_, newValue) => handleSliderChange(category.id, newValue)}
                                                aria-labelledby={`category-slider-${category.id}`}
                                                valueLabelDisplay="auto"
                                                valueLabelFormat={(value) => `${value.toFixed(1)}%`}
                                                step={0.1}
                                                marks
                                                min={0}
                                                max={100}
                                            />
                                        </Grid>

                                        <Grid item xs={12} sm={3}>
                                            <Box display="flex" alignItems="center">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => adjustAllocation(category.id, -1000)}
                                                    disabled={parseFloat(expenseAllocations[category.id] || 0) <= 0}
                                                >
                                                    <RemoveIcon />
                                                </IconButton>

                                                <TextField
                                                    value={expenseAllocations[category.id] || ""}
                                                    onChange={(e) => onAllocationChange(category.id, e.target.value)}
                                                    InputProps={{
                                                        endAdornment: <InputAdornment position="end">₽</InputAdornment>,
                                                        inputProps: { min: 0, style: { textAlign: 'right' } }
                                                    }}
                                                    variant="outlined"
                                                    size="small"
                                                    type="number"
                                                    sx={{ mx: 1, width: '120px' }}
                                                />

                                                <IconButton
                                                    size="small"
                                                    onClick={() => adjustAllocation(category.id, 1000)}
                                                >
                                                    <AddIcon />
                                                </IconButton>
                                            </Box>
                                        </Grid>
                                    </Grid>
                                </Paper>
                            ))}
                        </Stack>
                    )}
                </Grid>
            </Grid>
        </Box>
    );
};

export default BudgetCalculatorWidget; 
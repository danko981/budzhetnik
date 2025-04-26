import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    TextField,
    Grid,
    Card,
    CardContent,
    CardActions,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    LinearProgress,
    Divider,
    Alert,
    CircularProgress,
    IconButton,
    FormHelperText,
    Tabs,
    Tab,
    Stepper,
    Step,
    StepLabel,
    Autocomplete,
    InputAdornment
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    ArrowUpward as IncomeIcon,
    ArrowDownward as ExpenseIcon,
    AccountBalance as BudgetIcon,
    AttachMoney as MoneyIcon,
    DateRange as DateIcon
} from '@mui/icons-material';
import { budgetsAPI, categoriesAPI } from '../../services/api';
import BudgetCalculatorWidget from '../../components/BudgetCalculator/BudgetCalculatorWidget';

const Budgets = () => {
    // Состояния
    const [budgets, setBudgets] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [activeStep, setActiveStep] = useState(0);
    const [budgetForm, setBudgetForm] = useState({
        name: '',
        description: '',
        startDate: '',
        endDate: '',
        totalAmount: '',
        incomeCategories: [],
        expenseCategories: [],
        expenseAllocations: {}
    });
    const [isEditing, setIsEditing] = useState(false);
    const [currentBudgetId, setCurrentBudgetId] = useState(null);
    const [calculatedBalance, setCalculatedBalance] = useState(0);

    // Загрузка бюджетов и категорий
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [budgetsResponse, categoriesResponse] = await Promise.all([
                budgetsAPI.getAll(),
                categoriesAPI.getAll()
            ]);
            setBudgets(budgetsResponse.data || []);
            setCategories(categoriesResponse.data || []);
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Не удалось загрузить данные. Попробуйте позже.');
        } finally {
            setLoading(false);
        }
    };

    // Загрузка данных при монтировании компонента
    useEffect(() => {
        fetchData();
    }, []);

    // Расчет баланса при изменении формы бюджета
    useEffect(() => {
        calculateBalance();
    }, [budgetForm.totalAmount, budgetForm.expenseAllocations]);

    // Расчет баланса
    const calculateBalance = () => {
        const totalAmount = parseFloat(budgetForm.totalAmount) || 0;
        let allocatedTotal = 0;

        for (const categoryId in budgetForm.expenseAllocations) {
            allocatedTotal += parseFloat(budgetForm.expenseAllocations[categoryId] || 0);
        }

        setCalculatedBalance(totalAmount - allocatedTotal);
    };

    // Открытие диалога создания/редактирования бюджета
    const handleOpenDialog = (budget = null) => {
        if (budget) {
            // Форматируем даты для полей ввода
            const startDate = new Date(budget.startDate).toISOString().split('T')[0];
            const endDate = new Date(budget.endDate).toISOString().split('T')[0];

            setBudgetForm({
                name: budget.name,
                description: budget.description || '',
                startDate,
                endDate,
                totalAmount: budget.totalAmount.toString(),
                incomeCategories: budget.incomeCategories || [],
                expenseCategories: budget.expenseCategories || [],
                expenseAllocations: budget.expenseAllocations || {}
            });
            setCurrentBudgetId(budget.id);
            setIsEditing(true);
        } else {
            // Текущая дата для начала периода
            const today = new Date();
            // Конец периода - через месяц
            const nextMonth = new Date();
            nextMonth.setMonth(nextMonth.getMonth() + 1);

            setBudgetForm({
                name: '',
                description: '',
                startDate: today.toISOString().split('T')[0],
                endDate: nextMonth.toISOString().split('T')[0],
                totalAmount: '',
                incomeCategories: [],
                expenseCategories: [],
                expenseAllocations: {}
            });
            setIsEditing(false);
            setCurrentBudgetId(null);
        }
        setActiveStep(0);
        setDialogOpen(true);
    };

    // Закрытие диалога
    const handleCloseDialog = () => {
        setDialogOpen(false);
        setActiveStep(0);
        setBudgetForm({
            name: '',
            description: '',
            startDate: '',
            endDate: '',
            totalAmount: '',
            incomeCategories: [],
            expenseCategories: [],
            expenseAllocations: {}
        });
    };

    // Обработка изменений в форме
    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setBudgetForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Обработка изменения категорий доходов
    const handleIncomeChange = (event, newValue) => {
        setBudgetForm(prev => ({
            ...prev,
            incomeCategories: newValue
        }));
    };

    // Обработка изменения категорий расходов
    const handleExpenseChange = (event, newValue) => {
        // Создаем новый объект распределения расходов только для выбранных категорий
        const newAllocations = {};

        // Сохраняем существующие распределения для категорий, которые остаются выбранными
        newValue.forEach(category => {
            if (budgetForm.expenseAllocations[category.id]) {
                newAllocations[category.id] = budgetForm.expenseAllocations[category.id];
            } else {
                newAllocations[category.id] = "0";
            }
        });

        setBudgetForm(prev => ({
            ...prev,
            expenseCategories: newValue,
            expenseAllocations: newAllocations
        }));
    };

    // Обработка изменения распределения расходов
    const handleAllocationChange = (categoryId, value) => {
        setBudgetForm(prev => ({
            ...prev,
            expenseAllocations: {
                ...prev.expenseAllocations,
                [categoryId]: value
            }
        }));
    };

    // Переход к следующему шагу
    const handleNext = () => {
        setActiveStep(prev => prev + 1);
    };

    // Переход к предыдущему шагу
    const handleBack = () => {
        setActiveStep(prev => prev - 1);
    };

    // Проверка валидности текущего шага
    const isStepValid = () => {
        switch (activeStep) {
            case 0: // Основная информация
                return budgetForm.name.trim() !== '' &&
                    budgetForm.startDate !== '' &&
                    budgetForm.endDate !== '';
            case 1: // Категории доходов
                return budgetForm.incomeCategories.length > 0 &&
                    budgetForm.totalAmount.trim() !== '';
            case 2: // Категории расходов
                return budgetForm.expenseCategories.length > 0;
            case 3: // Распределение бюджета
                // Проверяем, что все распределения введены и сумма не превышает общий бюджет
                const totalAllocated = Object.values(budgetForm.expenseAllocations)
                    .reduce((sum, value) => sum + parseFloat(value || 0), 0);
                return totalAllocated <= parseFloat(budgetForm.totalAmount);
            default:
                return true;
        }
    };

    // Получение списка шагов
    const getSteps = () => {
        return ['Информация', 'Доходы', 'Расходы', 'Распределение'];
    };

    // Сохранение бюджета
    const handleSaveBudget = async () => {
        setLoading(true);
        setError(null);
        try {
            const budgetData = {
                ...budgetForm,
                totalAmount: parseFloat(budgetForm.totalAmount),
                // Преобразуем строковые значения распределения в числовые
                expenseAllocations: Object.entries(budgetForm.expenseAllocations).reduce(
                    (acc, [key, value]) => {
                        acc[key] = parseFloat(value);
                        return acc;
                    },
                    {}
                )
            };

            if (isEditing) {
                await budgetsAPI.update(currentBudgetId, budgetData);
            } else {
                await budgetsAPI.create(budgetData);
            }
            fetchData();
            handleCloseDialog();
        } catch (err) {
            console.error('Error saving budget:', err);
            setError('Не удалось сохранить бюджет. Попробуйте позже.');
        } finally {
            setLoading(false);
        }
    };

    // Удаление бюджета
    const handleDeleteBudget = async (id) => {
        if (!window.confirm('Вы уверены, что хотите удалить этот бюджет?')) {
            return;
        }

        setLoading(true);
        setError(null);
        try {
            await budgetsAPI.delete(id);
            fetchData();
        } catch (err) {
            console.error('Error deleting budget:', err);
            setError('Не удалось удалить бюджет.');
        } finally {
            setLoading(false);
        }
    };

    // Получение содержимого шага
    const getStepContent = (step) => {
        switch (step) {
            case 0: // Основная информация
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Название бюджета"
                                name="name"
                                value={budgetForm.name}
                                onChange={handleFormChange}
                                required
                                placeholder="Например: Бюджет на май 2025"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Описание"
                                name="description"
                                value={budgetForm.description}
                                onChange={handleFormChange}
                                multiline
                                rows={2}
                                placeholder="Дополнительная информация о бюджете"
                            />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Дата начала"
                                name="startDate"
                                type="date"
                                value={budgetForm.startDate}
                                onChange={handleFormChange}
                                required
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Дата окончания"
                                name="endDate"
                                type="date"
                                value={budgetForm.endDate}
                                onChange={handleFormChange}
                                required
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>
                    </Grid>
                );
            case 1: // Категории доходов
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Autocomplete
                                multiple
                                id="income-categories"
                                options={categories.filter(cat => cat.type === 'income')}
                                getOptionLabel={(option) => option.name}
                                value={budgetForm.incomeCategories}
                                onChange={handleIncomeChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        variant="outlined"
                                        label="Категории доходов"
                                        placeholder="Выберите категории"
                                    />
                                )}
                                renderTags={(value, getTagProps) =>
                                    value.map((option, index) => (
                                        <Chip
                                            key={option.id}
                                            label={option.name}
                                            {...getTagProps({ index })}
                                            style={{
                                                backgroundColor: option.color || '#e0e0e0',
                                                color: option.color ? '#fff' : 'inherit'
                                            }}
                                        />
                                    ))
                                }
                                noOptionsText="Нет доступных категорий доходов"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Общая сумма бюджета"
                                name="totalAmount"
                                value={budgetForm.totalAmount}
                                onChange={handleFormChange}
                                required
                                type="number"
                                InputProps={{
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <MoneyIcon />
                                        </InputAdornment>
                                    ),
                                }}
                                placeholder="Введите сумму в рублях"
                            />
                        </Grid>
                    </Grid>
                );
            case 2: // Категории расходов
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Autocomplete
                                multiple
                                id="expense-categories"
                                options={categories.filter(cat => cat.type === 'expense')}
                                getOptionLabel={(option) => option.name}
                                value={budgetForm.expenseCategories}
                                onChange={handleExpenseChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        variant="outlined"
                                        label="Категории расходов"
                                        placeholder="Выберите категории"
                                    />
                                )}
                                renderTags={(value, getTagProps) =>
                                    value.map((option, index) => (
                                        <Chip
                                            key={option.id}
                                            label={option.name}
                                            {...getTagProps({ index })}
                                            style={{
                                                backgroundColor: option.color || '#e0e0e0',
                                                color: option.color ? '#fff' : 'inherit'
                                            }}
                                        />
                                    ))
                                }
                                noOptionsText="Нет доступных категорий расходов"
                            />
                        </Grid>
                    </Grid>
                );
            case 3: // Распределение бюджета
                return (
                    <BudgetCalculatorWidget
                        totalAmount={budgetForm.totalAmount}
                        expenseCategories={budgetForm.expenseCategories}
                        expenseAllocations={budgetForm.expenseAllocations}
                        onAllocationChange={handleAllocationChange}
                        startDate={budgetForm.startDate}
                        endDate={budgetForm.endDate}
                    />
                );
            default:
                return 'Неизвестный шаг';
        }
    };

    // Расчет процента выполнения бюджета
    const calculateBudgetProgress = (budget) => {
        if (!budget.totalAmount) return 0;

        // В реальной реализации здесь будет расчет на основе фактических расходов
        // Сейчас возвращаем случайное значение для демонстрации
        return Math.min(Math.floor(Math.random() * 100), 100);
    };

    // Получение цвета прогресса в зависимости от значения
    const getProgressColor = (progress) => {
        if (progress > 90) return 'error';
        if (progress > 70) return 'warning';
        return 'success';
    };

    // Форматирование даты
    const formatDate = (dateString) => {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('ru-RU', options);
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Бюджеты
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Создать бюджет
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {loading && !dialogOpen ? (
                <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    {budgets.length === 0 ? (
                        <Paper sx={{ p: 3, textAlign: 'center' }}>
                            <Typography>
                                У вас пока нет бюджетов. Создайте первый бюджет, чтобы начать контролировать свои финансы.
                            </Typography>
                        </Paper>
                    ) : (
                        <Grid container spacing={3}>
                            {budgets.map(budget => {
                                const progress = calculateBudgetProgress(budget);
                                const progressColor = getProgressColor(progress);

                                return (
                                    <Grid item xs={12} sm={6} md={4} key={budget.id}>
                                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                            <CardContent sx={{ flexGrow: 1 }}>
                                                <Typography variant="h6" component="div" gutterBottom>
                                                    {budget.name}
                                                </Typography>

                                                <Box display="flex" alignItems="center" mb={1}>
                                                    <DateIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                                    <Typography variant="body2" color="text.secondary">
                                                        {formatDate(budget.startDate)} - {formatDate(budget.endDate)}
                                                    </Typography>
                                                </Box>

                                                <Box display="flex" alignItems="center" mb={2}>
                                                    <MoneyIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                                    <Typography variant="body2" color="text.secondary">
                                                        Бюджет: {budget.totalAmount.toLocaleString('ru-RU')} ₽
                                                    </Typography>
                                                </Box>

                                                {budget.description && (
                                                    <Typography variant="body2" color="text.secondary" mb={2}>
                                                        {budget.description}
                                                    </Typography>
                                                )}

                                                <Box sx={{ mb: 2 }}>
                                                    <Typography variant="body2" display="flex" justifyContent="space-between">
                                                        <span>Выполнение:</span>
                                                        <span>{progress}%</span>
                                                    </Typography>
                                                    <LinearProgress
                                                        variant="determinate"
                                                        value={progress}
                                                        color={progressColor}
                                                        sx={{ height: 8, borderRadius: 4, mt: 1 }}
                                                    />
                                                </Box>

                                                <Box>
                                                    <Typography variant="body2" gutterBottom>
                                                        Категории расходов:
                                                    </Typography>
                                                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                                                        {budget.expenseCategories.map(category => (
                                                            <Chip
                                                                key={category.id}
                                                                label={category.name}
                                                                size="small"
                                                                sx={{
                                                                    bgcolor: category.color || 'default',
                                                                    color: 'white',
                                                                    mb: 0.5
                                                                }}
                                                            />
                                                        ))}
                                                        {budget.expenseCategories.length === 0 && (
                                                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                                                Нет категорий
                                                            </Typography>
                                                        )}
                                                    </Box>
                                                </Box>
                                            </CardContent>
                                            <CardActions>
                                                <Button
                                                    size="small"
                                                    startIcon={<EditIcon />}
                                                    onClick={() => handleOpenDialog(budget)}
                                                >
                                                    Изменить
                                                </Button>
                                                <Button
                                                    size="small"
                                                    color="error"
                                                    startIcon={<DeleteIcon />}
                                                    onClick={() => handleDeleteBudget(budget.id)}
                                                >
                                                    Удалить
                                                </Button>
                                            </CardActions>
                                        </Card>
                                    </Grid>
                                );
                            })}
                        </Grid>
                    )}
                </>
            )}

            {/* Диалог создания/редактирования бюджета */}
            <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
                <DialogTitle>
                    {isEditing ? 'Редактирование бюджета' : 'Создание нового бюджета'}
                </DialogTitle>
                <DialogContent>
                    <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
                        {getSteps().map((label) => (
                            <Step key={label}>
                                <StepLabel>{label}</StepLabel>
                            </Step>
                        ))}
                    </Stepper>

                    {getStepContent(activeStep)}

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Отмена</Button>
                    {activeStep > 0 && (
                        <Button onClick={handleBack}>
                            Назад
                        </Button>
                    )}
                    {activeStep < getSteps().length - 1 ? (
                        <Button
                            variant="contained"
                            onClick={handleNext}
                            disabled={!isStepValid()}
                        >
                            Далее
                        </Button>
                    ) : (
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleSaveBudget}
                            disabled={loading || !isStepValid()}
                        >
                            {loading ? <CircularProgress size={24} /> : 'Сохранить'}
                        </Button>
                    )}
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Budgets; 
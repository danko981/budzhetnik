import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Tabs,
    Tab,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Card,
    CardContent,
    Divider,
    Alert,
    CircularProgress,
    Button,
    TextField,
    IconButton
} from '@mui/material';
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line,
    AreaChart,
    Area
} from 'recharts';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ruLocale from 'date-fns/locale/ru';
import {
    FilterAlt as FilterIcon,
    GetApp as DownloadIcon,
    RotateLeft as ResetIcon
} from '@mui/icons-material';
import { reportsAPI, budgetsAPI, categoriesAPI } from '../../services/api';

// Генерация данных для диаграмм
const generateChartData = () => {
    // Это временный пример данных, в реальном приложении данные будут получены с сервера
    const categoryData = [
        { name: 'Продукты', value: 35000, color: '#4caf50' },
        { name: 'Транспорт', value: 12000, color: '#2196f3' },
        { name: 'Развлечения', value: 18000, color: '#ff9800' },
        { name: 'Коммунальные платежи', value: 20000, color: '#e91e63' },
        { name: 'Прочее', value: 15000, color: '#9c27b0' }
    ];

    const monthlyData = [
        { name: 'Янв', доходы: 90000, расходы: 85000 },
        { name: 'Фев', доходы: 85000, расходы: 83000 },
        { name: 'Мар', доходы: 88000, расходы: 84000 },
        { name: 'Апр', доходы: 92000, расходы: 87000 },
        { name: 'Май', доходы: 95000, расходы: 88000 },
        { name: 'Июн', доходы: 93000, расходы: 90000 }
    ];

    const budgetPerformanceData = [
        { name: 'Продукты', план: 40000, факт: 35000 },
        { name: 'Транспорт', план: 15000, факт: 12000 },
        { name: 'Развлечения', план: 20000, факт: 18000 },
        { name: 'Коммунальные платежи', план: 25000, факт: 20000 },
        { name: 'Прочее', план: 10000, факт: 15000 }
    ];

    return { categoryData, monthlyData, budgetPerformanceData };
};

const Reports = () => {
    // Состояния
    const [tabValue, setTabValue] = useState(0);
    const [budgets, setBudgets] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedBudget, setSelectedBudget] = useState('');
    const [dateRange, setDateRange] = useState({
        startDate: new Date(new Date().getFullYear(), new Date().getMonth() - 3, 1),
        endDate: new Date()
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [chartData, setChartData] = useState({
        categoryData: [],
        monthlyData: [],
        budgetPerformanceData: []
    });

    // Загрузка данных для отчетов
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            // В реальном приложении здесь будет запрос к API для получения данных отчетов
            // Сейчас используем временные данные для демонстрации
            const [budgetsResponse, categoriesResponse] = await Promise.all([
                budgetsAPI.getAll(),
                categoriesAPI.getAll()
            ]);

            setBudgets(budgetsResponse.data || []);
            setCategories(categoriesResponse.data || []);

            // Используем временные данные для диаграмм
            setChartData(generateChartData());

        } catch (err) {
            console.error('Error fetching report data:', err);
            setError('Не удалось загрузить данные отчетов. Попробуйте позже.');
        } finally {
            setLoading(false);
        }
    };

    // Загрузка данных при монтировании компонента
    useEffect(() => {
        fetchData();
    }, []);

    // Обработка изменения вкладки
    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    // Обработка изменения выбранного бюджета
    const handleBudgetChange = (event) => {
        setSelectedBudget(event.target.value);
    };

    // Обработка сброса фильтров
    const handleResetFilters = () => {
        setSelectedBudget('');
        setDateRange({
            startDate: new Date(new Date().getFullYear(), new Date().getMonth() - 3, 1),
            endDate: new Date()
        });
    };

    // Форматирование суммы для отображения
    const formatAmount = (amount) => {
        return amount.toLocaleString('ru-RU') + ' ₽';
    };

    // Получение общей суммы доходов
    const getTotalIncome = () => {
        return chartData.monthlyData.reduce((sum, item) => sum + item.доходы, 0);
    };

    // Получение общей суммы расходов
    const getTotalExpenses = () => {
        return chartData.monthlyData.reduce((sum, item) => sum + item.расходы, 0);
    };

    // Получение баланса
    const getBalance = () => {
        return getTotalIncome() - getTotalExpenses();
    };

    // Получение содержимого текущей вкладки
    const getTabContent = () => {
        switch (tabValue) {
            case 0: // Обзор
                return (
                    <Grid container spacing={3}>
                        {/* Карточки с общей информацией */}
                        <Grid item xs={12} md={4}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Общий доход
                                    </Typography>
                                    <Typography variant="h4" color="success.main">
                                        {formatAmount(getTotalIncome())}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Общий расход
                                    </Typography>
                                    <Typography variant="h4" color="error.main">
                                        {formatAmount(getTotalExpenses())}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Баланс
                                    </Typography>
                                    <Typography
                                        variant="h4"
                                        color={getBalance() >= 0 ? 'success.main' : 'error.main'}
                                    >
                                        {formatAmount(getBalance())}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* График доходов и расходов по месяцам */}
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Динамика доходов и расходов
                                </Typography>
                                <Divider sx={{ mb: 2 }} />
                                <Box sx={{ height: 300 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart
                                            data={chartData.monthlyData}
                                            margin={{ top: 10, right: 30, left: 20, bottom: 0 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip formatter={(value) => formatAmount(value)} />
                                            <Legend />
                                            <Area
                                                type="monotone"
                                                dataKey="доходы"
                                                stackId="1"
                                                stroke="#4caf50"
                                                fill="#4caf50"
                                                fillOpacity={0.6}
                                                name="Доходы"
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey="расходы"
                                                stackId="2"
                                                stroke="#f44336"
                                                fill="#f44336"
                                                fillOpacity={0.6}
                                                name="Расходы"
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </Box>
                            </Paper>
                        </Grid>
                    </Grid>
                );

            case 1: // Расходы по категориям
                return (
                    <Grid container spacing={3}>
                        {/* График расходов по категориям */}
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 3, height: '100%' }}>
                                <Typography variant="h6" gutterBottom>
                                    Структура расходов
                                </Typography>
                                <Divider sx={{ mb: 2 }} />
                                <Box sx={{ height: 300, display: 'flex', justifyContent: 'center' }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={chartData.categoryData}
                                                cx="50%"
                                                cy="50%"
                                                labelLine={false}
                                                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                                outerRadius={80}
                                                fill="#8884d8"
                                                dataKey="value"
                                                nameKey="name"
                                            >
                                                {chartData.categoryData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(value) => formatAmount(value)} />
                                            <Legend />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </Box>
                            </Paper>
                        </Grid>

                        {/* Таблица расходов по категориям */}
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 3, height: '100%' }}>
                                <Typography variant="h6" gutterBottom>
                                    Расходы по категориям
                                </Typography>
                                <Divider sx={{ mb: 2 }} />
                                <Box sx={{ overflowX: 'auto' }}>
                                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Категория</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>Сумма</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>% от общего</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {chartData.categoryData.map((category, index) => {
                                                const totalExpenses = chartData.categoryData.reduce((sum, item) => sum + item.value, 0);
                                                const percentage = (category.value / totalExpenses * 100).toFixed(1);

                                                return (
                                                    <tr key={index}>
                                                        <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            <Box display="flex" alignItems="center">
                                                                <Box
                                                                    sx={{
                                                                        width: 16,
                                                                        height: 16,
                                                                        borderRadius: '50%',
                                                                        bgcolor: category.color,
                                                                        mr: 1
                                                                    }}
                                                                />
                                                                {category.name}
                                                            </Box>
                                                        </td>
                                                        <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            {formatAmount(category.value)}
                                                        </td>
                                                        <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            {percentage}%
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                        <tfoot>
                                            <tr>
                                                <td style={{ fontWeight: 'bold', padding: '8px', borderTop: '2px solid #ddd' }}>Итого</td>
                                                <td style={{ fontWeight: 'bold', textAlign: 'right', padding: '8px', borderTop: '2px solid #ddd' }}>
                                                    {formatAmount(chartData.categoryData.reduce((sum, item) => sum + item.value, 0))}
                                                </td>
                                                <td style={{ textAlign: 'right', padding: '8px', borderTop: '2px solid #ddd' }}>100%</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </Box>
                            </Paper>
                        </Grid>
                    </Grid>
                );

            case 2: // Выполнение бюджета
                return (
                    <Grid container spacing={3}>
                        {/* График выполнения бюджета */}
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Выполнение бюджета по категориям
                                </Typography>
                                <Divider sx={{ mb: 2 }} />
                                <Box sx={{ height: 400 }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart
                                            data={chartData.budgetPerformanceData}
                                            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip formatter={(value) => formatAmount(value)} />
                                            <Legend />
                                            <Bar
                                                dataKey="план"
                                                stackId="a"
                                                fill="#8884d8"
                                                name="План"
                                            />
                                            <Bar
                                                dataKey="факт"
                                                stackId="a"
                                                fill="#82ca9d"
                                                name="Факт"
                                            />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </Box>
                            </Paper>
                        </Grid>

                        {/* Таблица выполнения бюджета */}
                        <Grid item xs={12}>
                            <Paper sx={{ p: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Анализ выполнения бюджета
                                </Typography>
                                <Divider sx={{ mb: 2 }} />
                                <Box sx={{ overflowX: 'auto' }}>
                                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #ddd' }}>Категория</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>План</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>Факт</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>Разница</th>
                                                <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>Выполнение</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {chartData.budgetPerformanceData.map((item, index) => {
                                                const diff = item.план - item.факт;
                                                const performance = item.план > 0 ? (item.факт / item.план * 100).toFixed(1) : 0;

                                                return (
                                                    <tr key={index}>
                                                        <td style={{ padding: '8px', borderBottom: '1px solid #ddd' }}>{item.name}</td>
                                                        <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            {formatAmount(item.план)}
                                                        </td>
                                                        <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            {formatAmount(item.факт)}
                                                        </td>
                                                        <td style={{
                                                            textAlign: 'right',
                                                            padding: '8px',
                                                            borderBottom: '1px solid #ddd',
                                                            color: diff >= 0 ? 'green' : 'red'
                                                        }}>
                                                            {formatAmount(Math.abs(diff))} {diff >= 0 ? '(экономия)' : '(перерасход)'}
                                                        </td>
                                                        <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #ddd' }}>
                                                            {performance}%
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                        <tfoot>
                                            <tr>
                                                <td style={{ fontWeight: 'bold', padding: '8px', borderTop: '2px solid #ddd' }}>Итого</td>
                                                <td style={{ fontWeight: 'bold', textAlign: 'right', padding: '8px', borderTop: '2px solid #ddd' }}>
                                                    {formatAmount(chartData.budgetPerformanceData.reduce((sum, item) => sum + item.план, 0))}
                                                </td>
                                                <td style={{ fontWeight: 'bold', textAlign: 'right', padding: '8px', borderTop: '2px solid #ddd' }}>
                                                    {formatAmount(chartData.budgetPerformanceData.reduce((sum, item) => sum + item.факт, 0))}
                                                </td>
                                                <td style={{
                                                    fontWeight: 'bold',
                                                    textAlign: 'right',
                                                    padding: '8px',
                                                    borderTop: '2px solid #ddd',
                                                    color: chartData.budgetPerformanceData.reduce((sum, item) => sum + item.план, 0) - chartData.budgetPerformanceData.reduce((sum, item) => sum + item.факт, 0) >= 0 ? 'green' : 'red'
                                                }}>
                                                    {formatAmount(Math.abs(
                                                        chartData.budgetPerformanceData.reduce((sum, item) => sum + item.план, 0) -
                                                        chartData.budgetPerformanceData.reduce((sum, item) => sum + item.факт, 0)
                                                    ))} {
                                                        chartData.budgetPerformanceData.reduce((sum, item) => sum + item.план, 0) -
                                                            chartData.budgetPerformanceData.reduce((sum, item) => sum + item.факт, 0) >= 0 ?
                                                            '(экономия)' : '(перерасход)'
                                                    }
                                                </td>
                                                <td style={{ fontWeight: 'bold', textAlign: 'right', padding: '8px', borderTop: '2px solid #ddd' }}>
                                                    {(
                                                        chartData.budgetPerformanceData.reduce((sum, item) => sum + item.факт, 0) /
                                                        chartData.budgetPerformanceData.reduce((sum, item) => sum + item.план, 0) * 100
                                                    ).toFixed(1)}%
                                                </td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </Box>
                            </Paper>
                        </Grid>
                    </Grid>
                );

            default:
                return null;
        }
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Отчеты
                </Typography>
                <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                >
                    Экспорт
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {/* Фильтры */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                        <FormControl fullWidth>
                            <InputLabel>Бюджет</InputLabel>
                            <Select
                                value={selectedBudget}
                                onChange={handleBudgetChange}
                                label="Бюджет"
                            >
                                <MenuItem value="">Все бюджеты</MenuItem>
                                {budgets.map(budget => (
                                    <MenuItem key={budget.id} value={budget.id}>
                                        {budget.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ruLocale}>
                            <DatePicker
                                label="Начало периода"
                                value={dateRange.startDate}
                                onChange={(date) => setDateRange(prev => ({ ...prev, startDate: date }))}
                                slotProps={{ textField: { fullWidth: true } }}
                                format="dd.MM.yyyy"
                            />
                        </LocalizationProvider>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ruLocale}>
                            <DatePicker
                                label="Конец периода"
                                value={dateRange.endDate}
                                onChange={(date) => setDateRange(prev => ({ ...prev, endDate: date }))}
                                slotProps={{ textField: { fullWidth: true } }}
                                format="dd.MM.yyyy"
                            />
                        </LocalizationProvider>
                    </Grid>
                    <Grid item xs={12} md={2} display="flex" justifyContent="center">
                        <IconButton onClick={handleResetFilters} title="Сбросить фильтры">
                            <ResetIcon />
                        </IconButton>
                    </Grid>
                </Grid>
            </Paper>

            {/* Вкладки отчетов */}
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={tabValue}
                    onChange={handleTabChange}
                    indicatorColor="primary"
                    textColor="primary"
                    variant="fullWidth"
                >
                    <Tab label="Обзор" />
                    <Tab label="Расходы по категориям" />
                    <Tab label="Выполнение бюджета" />
                </Tabs>
            </Paper>

            {loading ? (
                <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress />
                </Box>
            ) : (
                getTabContent()
            )}
        </Box>
    );
};

export default Reports; 
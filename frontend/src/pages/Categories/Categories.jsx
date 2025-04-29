import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    TextField,
    Grid,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    Divider,
    Alert,
    CircularProgress,
    Autocomplete,
    Collapse,
    Tooltip,
    ListItemButton
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    ArrowUpward as IncomeIcon,
    ArrowDownward as ExpenseIcon,
    LocalOffer as TagIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Bookmark as SubcategoryIcon
} from '@mui/icons-material';
import { categoriesAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

// Цвета для категорий
const CATEGORY_COLORS = [
    '#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5',
    '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50',
    '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107', '#ff9800'
];

// Предопределенные теги
const PREDEFINED_TAGS = [
    'Регулярные', 'Важные', 'Отложенные', 'Необязательные',
    'Семья', 'Работа', 'Дом', 'Транспорт', 'Еда', 'Здоровье',
    'Развлечения', 'Отпуск', 'Образование', 'Хобби'
];

const Categories = () => {
    // Состояния
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [categoryForm, setCategoryForm] = useState({
        name: '',
        type: 'expense',
        color: CATEGORY_COLORS[0],
        icon: 'default',
        tags: [],
        parentId: null,
        isSubcategory: false
    });
    const [isEditing, setIsEditing] = useState(false);
    const [currentCategoryId, setCurrentCategoryId] = useState(null);
    const [expandedCategories, setExpandedCategories] = useState({});
    const [subcategoryDialogOpen, setSubcategoryDialogOpen] = useState(false);
    const [parentCategory, setParentCategory] = useState(null);
    const { user } = useAuth();

    // Загрузка категорий
    const fetchCategories = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await categoriesAPI.getAll();
            setCategories(response.data || []);
        } catch (err) {
            console.error('Error fetching categories:', err);
            setError('Не удалось загрузить категории. Попробуйте позже.');
        } finally {
            setLoading(false);
        }
    };

    // Загрузка категорий при монтировании компонента
    useEffect(() => {
        fetchCategories();
    }, []);

    // Переключение свернутого/развернутого состояния категории
    const toggleCategoryExpanded = (categoryId) => {
        setExpandedCategories(prev => ({
            ...prev,
            [categoryId]: !prev[categoryId]
        }));
    };

    // Открытие диалога создания/редактирования категории
    const handleOpenDialog = (category = null) => {
        if (category) {
            setCategoryForm({
                name: category.name,
                type: category.type,
                color: category.color || CATEGORY_COLORS[0],
                icon: category.icon || 'default',
                tags: category.tags || [],
                parentId: category.parentId || null,
                isSubcategory: !!category.parentId
            });
            setCurrentCategoryId(category.id);
            setIsEditing(true);
        } else {
            setCategoryForm({
                name: '',
                type: 'expense',
                color: CATEGORY_COLORS[0],
                icon: 'default',
                tags: [],
                parentId: null,
                isSubcategory: false
            });
            setIsEditing(false);
            setCurrentCategoryId(null);
        }
        setDialogOpen(true);
    };

    // Открытие диалога создания подкатегории
    const handleOpenSubcategoryDialog = (parentCategory) => {
        setParentCategory(parentCategory);
        setCategoryForm({
            name: '',
            type: parentCategory.type, // Наследуем тип родительской категории
            color: parentCategory.color,
            icon: 'default',
            tags: [],
            parentId: parentCategory.id,
            isSubcategory: true
        });
        setIsEditing(false);
        setCurrentCategoryId(null);
        setSubcategoryDialogOpen(true);
    };

    // Закрытие диалога
    const handleCloseDialog = () => {
        setDialogOpen(false);
        setSubcategoryDialogOpen(false);
        setCategoryForm({
            name: '',
            type: 'expense',
            color: CATEGORY_COLORS[0],
            icon: 'default',
            tags: [],
            parentId: null,
            isSubcategory: false
        });
        setParentCategory(null);
    };

    // Обработка изменений в форме
    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setCategoryForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Обработка изменений тегов
    const handleTagsChange = (event, newValue) => {
        setCategoryForm(prev => ({
            ...prev,
            tags: newValue
        }));
    };

    // Сохранение категории
    const handleSaveCategory = async () => {
        if (!categoryForm.name.trim()) {
            setError('Название категории не может быть пустым');
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const categoryData = { ...categoryForm, user_id: user?.id };

            if (isEditing) {
                await categoriesAPI.update(currentCategoryId, categoryData);
            } else {
                await categoriesAPI.create(categoryData);
            }
            fetchCategories();
            handleCloseDialog();
        } catch (err) {
            console.error('Error saving category:', err);
            setError('Не удалось сохранить категорию. Попробуйте позже.');
        } finally {
            setLoading(false);
        }
    };

    // Удаление категории
    const handleDeleteCategory = async (id) => {
        if (!window.confirm('Вы уверены, что хотите удалить эту категорию?')) {
            return;
        }

        setLoading(true);
        setError(null);
        try {
            await categoriesAPI.delete(id);
            fetchCategories();
        } catch (err) {
            console.error('Error deleting category:', err);
            setError('Не удалось удалить категорию. Возможно, она используется в бюджетах или транзакциях.');
        } finally {
            setLoading(false);
        }
    };

    // Получение имени типа категории
    const getCategoryTypeName = (type) => {
        return type === 'income' ? 'Доход' : 'Расход';
    };

    // Получение иконки типа категории
    const getCategoryTypeIcon = (type) => {
        return type === 'income' ? <IncomeIcon color="success" /> : <ExpenseIcon color="error" />;
    };

    // Фильтрация основных категорий (не подкатегорий)
    const filterMainCategories = (type) => {
        return categories.filter(cat => cat.type === type && !cat.parentId);
    };

    // Получение подкатегорий для данной категории
    const getSubcategoriesForCategory = (categoryId) => {
        return categories.filter(cat => cat.parentId === categoryId);
    };

    // Рендер категории
    const renderCategory = (category) => {
        const subcategories = getSubcategoriesForCategory(category.id);
        const hasSubcategories = subcategories.length > 0;
        const isExpanded = expandedCategories[category.id];

        return (
            <React.Fragment key={category.id}>
                <ListItem
                    sx={{
                        mb: 1,
                        bgcolor: 'background.paper',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'divider',
                    }}
                >
                    <Box
                        sx={{
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            bgcolor: category.color || '#ccc',
                            mr: 2
                        }}
                    />
                    <ListItemText
                        primary={
                            <Box display="flex" alignItems="center">
                                {category.name}
                                {category.tags && category.tags.length > 0 && (
                                    <Box ml={1} display="flex" flexWrap="wrap" gap={0.5}>
                                        {category.tags.map(tag => (
                                            <Chip
                                                key={tag}
                                                label={tag}
                                                size="small"
                                                icon={<TagIcon fontSize="small" />}
                                                sx={{ fontSize: '0.7rem' }}
                                            />
                                        ))}
                                    </Box>
                                )}
                            </Box>
                        }
                    />
                    <ListItemSecondaryAction>
                        {hasSubcategories && (
                            <IconButton edge="end" onClick={() => toggleCategoryExpanded(category.id)} size="small">
                                {isExpanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                            </IconButton>
                        )}
                        <Tooltip title="Добавить подкатегорию">
                            <IconButton edge="end" onClick={() => handleOpenSubcategoryDialog(category)} size="small">
                                <SubcategoryIcon fontSize="small" />
                            </IconButton>
                        </Tooltip>
                        <IconButton edge="end" onClick={() => handleOpenDialog(category)} size="small">
                            <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton edge="end" onClick={() => handleDeleteCategory(category.id)} size="small">
                            <DeleteIcon fontSize="small" />
                        </IconButton>
                    </ListItemSecondaryAction>
                </ListItem>

                {hasSubcategories && (
                    <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                        <Box pl={4}>
                            <List disablePadding>
                                {subcategories.map(subcategory => (
                                    <ListItem
                                        key={subcategory.id}
                                        sx={{
                                            mb: 1,
                                            bgcolor: 'background.paper',
                                            borderRadius: 1,
                                            border: '1px solid',
                                            borderColor: 'divider',
                                            borderStyle: 'dashed'
                                        }}
                                    >
                                        <Box
                                            sx={{
                                                width: 12,
                                                height: 12,
                                                borderRadius: '50%',
                                                bgcolor: subcategory.color || '#ccc',
                                                mr: 2
                                            }}
                                        />
                                        <ListItemText
                                            primary={
                                                <Box display="flex" alignItems="center">
                                                    {subcategory.name}
                                                    {subcategory.tags && subcategory.tags.length > 0 && (
                                                        <Box ml={1} display="flex" flexWrap="wrap" gap={0.5}>
                                                            {subcategory.tags.map(tag => (
                                                                <Chip
                                                                    key={tag}
                                                                    label={tag}
                                                                    size="small"
                                                                    icon={<TagIcon fontSize="small" />}
                                                                    sx={{ fontSize: '0.7rem' }}
                                                                />
                                                            ))}
                                                        </Box>
                                                    )}
                                                </Box>
                                            }
                                        />
                                        <ListItemSecondaryAction>
                                            <IconButton edge="end" onClick={() => handleOpenDialog(subcategory)} size="small">
                                                <EditIcon fontSize="small" />
                                            </IconButton>
                                            <IconButton edge="end" onClick={() => handleDeleteCategory(subcategory.id)} size="small">
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                ))}
                            </List>
                        </Box>
                    </Collapse>
                )}
            </React.Fragment>
        );
    };

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Категории
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Добавить категорию
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {loading && !dialogOpen ? (
                <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress />
                </Box>
            ) : (
                <>
                    {categories.length === 0 ? (
                        <Paper sx={{ p: 3, textAlign: 'center' }}>
                            <Typography>
                                У вас пока нет категорий. Создайте первую категорию, чтобы начать работу с бюджетами.
                            </Typography>
                        </Paper>
                    ) : (
                        <Grid container spacing={3}>
                            {/* Колонка доходов */}
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2, height: '100%' }}>
                                    <Typography variant="h6" color="success.main" display="flex" alignItems="center" mb={2}>
                                        <IncomeIcon sx={{ mr: 1 }} /> Доходы
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <List>
                                        {filterMainCategories('income').map(category => renderCategory(category))}
                                        {filterMainCategories('income').length === 0 && (
                                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center' }}>
                                                Нет категорий доходов
                                            </Typography>
                                        )}
                                    </List>
                                </Paper>
                            </Grid>

                            {/* Колонка расходов */}
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2, height: '100%' }}>
                                    <Typography variant="h6" color="error.main" display="flex" alignItems="center" mb={2}>
                                        <ExpenseIcon sx={{ mr: 1 }} /> Расходы
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <List>
                                        {filterMainCategories('expense').map(category => renderCategory(category))}
                                        {filterMainCategories('expense').length === 0 && (
                                            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center' }}>
                                                Нет категорий расходов
                                            </Typography>
                                        )}
                                    </List>
                                </Paper>
                            </Grid>
                        </Grid>
                    )}
                </>
            )}

            {/* Диалог создания/редактирования категории */}
            <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {isEditing ? 'Редактирование категории' : 'Создание новой категории'}
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Название категории"
                                name="name"
                                value={categoryForm.name}
                                onChange={handleFormChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControl fullWidth>
                                <InputLabel>Тип категории</InputLabel>
                                <Select
                                    name="type"
                                    value={categoryForm.type}
                                    onChange={handleFormChange}
                                    label="Тип категории"
                                    disabled={categoryForm.isSubcategory}
                                >
                                    <MenuItem value="income">Доход</MenuItem>
                                    <MenuItem value="expense">Расход</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12}>
                            <Autocomplete
                                multiple
                                freeSolo
                                options={PREDEFINED_TAGS}
                                value={categoryForm.tags}
                                onChange={handleTagsChange}
                                renderTags={(value, getTagProps) =>
                                    value.map((option, index) => (
                                        <Chip
                                            label={option}
                                            {...getTagProps({ index })}
                                            icon={<TagIcon />}
                                        />
                                    ))
                                }
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Теги"
                                        placeholder="Добавить тег"
                                        helperText="Добавьте теги для более удобной фильтрации"
                                    />
                                )}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <InputLabel sx={{ mb: 1 }}>Цвет категории</InputLabel>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                                {CATEGORY_COLORS.map(color => (
                                    <Box
                                        key={color}
                                        sx={{
                                            width: 36,
                                            height: 36,
                                            borderRadius: '50%',
                                            bgcolor: color,
                                            cursor: 'pointer',
                                            border: categoryForm.color === color ? '2px solid black' : 'none',
                                            '&:hover': {
                                                opacity: 0.8,
                                            }
                                        }}
                                        onClick={() => setCategoryForm(prev => ({ ...prev, color }))}
                                    />
                                ))}
                            </Box>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Отмена</Button>
                    <Button
                        onClick={handleSaveCategory}
                        variant="contained"
                        color="primary"
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Сохранить'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Диалог создания подкатегории */}
            <Dialog open={subcategoryDialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    Создание подкатегории для "{parentCategory?.name || ''}"
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Название подкатегории"
                                name="name"
                                value={categoryForm.name}
                                onChange={handleFormChange}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Typography variant="body2" color="text.secondary">
                                Тип: {getCategoryTypeName(categoryForm.type)}
                            </Typography>
                        </Grid>
                        <Grid item xs={12}>
                            <Autocomplete
                                multiple
                                freeSolo
                                options={PREDEFINED_TAGS}
                                value={categoryForm.tags}
                                onChange={handleTagsChange}
                                renderTags={(value, getTagProps) =>
                                    value.map((option, index) => (
                                        <Chip
                                            label={option}
                                            {...getTagProps({ index })}
                                            icon={<TagIcon />}
                                        />
                                    ))
                                }
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label="Теги"
                                        placeholder="Добавить тег"
                                        helperText="Добавьте теги для более удобной фильтрации"
                                    />
                                )}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <InputLabel sx={{ mb: 1 }}>Цвет подкатегории</InputLabel>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                                {CATEGORY_COLORS.map(color => (
                                    <Box
                                        key={color}
                                        sx={{
                                            width: 36,
                                            height: 36,
                                            borderRadius: '50%',
                                            bgcolor: color,
                                            cursor: 'pointer',
                                            border: categoryForm.color === color ? '2px solid black' : 'none',
                                            '&:hover': {
                                                opacity: 0.8,
                                            }
                                        }}
                                        onClick={() => setCategoryForm(prev => ({ ...prev, color }))}
                                    />
                                ))}
                            </Box>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Отмена</Button>
                    <Button
                        onClick={handleSaveCategory}
                        variant="contained"
                        color="primary"
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Сохранить'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Categories; 
import enum
from datetime import datetime, date
from typing import Optional, Any, List, Union
from werkzeug.security import generate_password_hash, check_password_hash
# Для пользовательской валидации
from sqlalchemy.orm import validates, relationship, backref
from . import db  # Импорт объекта db из __init__.py
from decimal import Decimal  # Для валидации денежных сумм

# --- Enums ---


class CategoryType(enum.Enum):
    """Тип категории: Доход или Расход."""
    INCOME = 'income'
    EXPENSE = 'expense'


class BudgetPeriod(enum.Enum):
    """Периодичность бюджета."""
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    SEMIANNUAL = 'semiannual'  # Полугодовой
    ANNUAL = 'annual'

# --- Модели ---


class User(db.Model):
    """Модель пользователя."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи: один пользователь может иметь много бюджетов, категорий, транзакций
    budgets = relationship(
        'Budget', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    categories = relationship(
        'Category', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    transactions = relationship(
        'Transaction', backref='owner', lazy='dynamic', cascade="all, delete-orphan")

    @validates('username')
    def validate_username(self, key: str, username: str) -> str:
        """Валидация имени пользователя."""
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return username.strip()

    @validates('email')
    def validate_email(self, key: str, email: str) -> str:
        """Валидация email."""
        if not email or '@' not in email:
            raise ValueError("Invalid email address.")
        return email.lower().strip()

    def set_password(self, password: str) -> None:
        """Устанавливает хешированный пароль."""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверяет предоставленный пароль с хешем."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Category(db.Model):
    """Модель категории доходов или расходов."""
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(CategoryType), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)

    # Связь: категория может иметь много транзакций
    transactions = relationship(
        'Transaction', backref='category', lazy='dynamic')

    # Ограничение: Имя категории должно быть уникально для пользователя и типа
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'name', 'type', name='_user_category_uc'),)

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Валидация имени категории."""
        if not name or len(name.strip()) < 1:
            raise ValueError("Category name cannot be empty.")
        return name.strip()

    def __repr__(self) -> str:
        return f'<Category {self.name} ({self.type.value}) for User {self.user_id}>'


class Budget(db.Model):
    """Модель бюджета на определенный период."""
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='Мой Бюджет')
    period = db.Column(db.Enum(BudgetPeriod), nullable=False,
                       default=BudgetPeriod.MONTHLY)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    # Целевая сумма (необязательно)
    target_amount = db.Column(db.Numeric(10, 2), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @validates('name')
    def validate_name(self, key: str, name: str) -> str:
        """Валидация имени бюджета."""
        if not name or len(name.strip()) < 1:
            raise ValueError("Budget name cannot be empty.")
        return name.strip()

    # Ограничение: Даты должны быть корректны
    @validates('start_date', 'end_date')
    def validate_dates(self, key: str, value: Any) -> date:
        if key == 'end_date' and self.start_date and value < self.start_date:
            raise ValueError("End date cannot be earlier than start date.")
        if key == 'start_date' and self.end_date and value > self.end_date:
            raise ValueError("Start date cannot be later than end date.")
        if not isinstance(value, date):
            # Пытаемся преобразовать, если это строка (может прийти из API)
            try:
                value = date.fromisoformat(str(value))
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid date format for {key}. Use YYYY-MM-DD.")
        return value

    @validates('target_amount')
    def validate_target_amount(self, key: str, value: Any) -> Optional[Decimal]:
        """Валидация целевой суммы."""
        if value is None:
            return None  # Целевая сумма необязательна

        # Преобразуем в Decimal для точности
        try:
            if not isinstance(value, Decimal):
                value = Decimal(str(value))
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format.")

        if value <= 0:
            raise ValueError("Target amount must be positive.")
        return value

    # Примечание: Связь с транзакциями будет неявной, через фильтрацию
    # транзакций пользователя по диапазону дат бюджета.

    def __repr__(self) -> str:
        return f'<Budget {self.name} ({self.period.value}) {self.start_date}-{self.end_date}>'


class Transaction(db.Model):
    """Модель финансовой транзакции (доход или расход)."""
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=True)
    # Используем Numeric для точности денежных сумм
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    # Тип транзакции должен совпадать с типом категории
    type = db.Column(db.Enum(CategoryType), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Внешние ключи
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)

    # Валидация суммы (должна быть > 0)
    @validates('amount')
    def validate_amount(self, key: str, amount: Any) -> Decimal:
        # Преобразуем в Decimal для сравнения
        try:
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
        except (ValueError, TypeError):
            raise ValueError("Invalid amount format.")

        if amount <= 0:
            raise ValueError("Amount must be positive.")
        return amount

    @validates('date')
    def validate_date(self, key: str, value: Any) -> date:
        """Валидация даты транзакции."""
        if not isinstance(value, date):
            try:
                value = date.fromisoformat(str(value))
            except (TypeError, ValueError):
                raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        return value

    # Валидация типа транзакции относительно категории
    # Вызывается при установке category_id или type
    @validates('category_id', 'type')
    def validate_category_type(self, key: str, value: Any) -> Any:
        category = None
        transaction_type = None

        if key == 'category_id':
            category = Category.query.get(value)
            transaction_type = self.type  # Используем текущий тип транзакции
        elif key == 'type':
            transaction_type = value
            if self.category_id:  # Если категория уже установлена
                category = Category.query.get(self.category_id)

        if category and transaction_type and category.type != transaction_type:
            raise ValueError(
                f"Transaction type '{transaction_type.value}' must match category type '{category.type.value}'.")

        # Если устанавливаем категорию, автоматически установим тип транзакции
        if key == 'category_id' and category:
            self.type = category.type

        return value

    def __repr__(self) -> str:
        sign = '+' if self.type == CategoryType.INCOME else '-'
        return f'<Transaction {self.id} ({sign}{self.amount} on {self.date}) Category: {self.category_id}>'

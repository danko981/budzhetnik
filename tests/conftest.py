import os
import pytest
import tempfile
from datetime import date, timedelta
from decimal import Decimal

from .. import create_app, db
from ..models import User, Category, Transaction, Budget, CategoryType, BudgetPeriod


@pytest.fixture
def app():
    """Создает и настраивает тестовое приложение Flask."""
    # Создаем временную БД файл
    db_fd, db_path = tempfile.mkstemp()

    app = create_app('testing')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-key',
    })

    # Создаем контекст приложения
    with app.app_context():
        # Создаем таблицы базы данных
        db.create_all()
        # Создаем тестовые данные
        _populate_test_data()

        yield app  # Возвращаем приложение для тестов

    # Закрываем и удаляем временный файл БД
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Создает тестовый клиент для приложения."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Предоставляет заголовки аутентификации для тестового пользователя."""
    # Выполняем вход и получаем токен
    response = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })

    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


def _populate_test_data():
    """Создает тестовые данные в базе."""
    # Создаем тестового пользователя
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Создаем тестовые категории
    categories = [
        Category(name='Зарплата', type=CategoryType.INCOME, user_id=user.id),
        Category(name='Подработка', type=CategoryType.INCOME, user_id=user.id),
        Category(name='Продукты', type=CategoryType.EXPENSE, user_id=user.id),
        Category(name='Транспорт', type=CategoryType.EXPENSE, user_id=user.id)
    ]
    db.session.add_all(categories)
    db.session.commit()

    # Создаем тестовые транзакции
    today = date.today()
    transactions = [
        Transaction(
            description='Основная зарплата',
            amount=Decimal('50000.00'),
            date=today - timedelta(days=15),
            type=CategoryType.INCOME,
            category_id=categories[0].id,
            user_id=user.id
        ),
        Transaction(
            description='Фриланс проект',
            amount=Decimal('15000.00'),
            date=today - timedelta(days=10),
            type=CategoryType.INCOME,
            category_id=categories[1].id,
            user_id=user.id
        ),
        Transaction(
            description='Покупка в супермаркете',
            amount=Decimal('3500.50'),
            date=today - timedelta(days=5),
            type=CategoryType.EXPENSE,
            category_id=categories[2].id,
            user_id=user.id
        ),
        Transaction(
            description='Такси',
            amount=Decimal('450.00'),
            date=today - timedelta(days=2),
            type=CategoryType.EXPENSE,
            category_id=categories[3].id,
            user_id=user.id
        )
    ]
    db.session.add_all(transactions)

    # Создаем тестовый бюджет
    budget = Budget(
        name='Тестовый бюджет',
        period=BudgetPeriod.MONTHLY,
        start_date=today.replace(day=1),  # Первый день текущего месяца
        end_date=(today.replace(day=1) + timedelta(days=31)
                  # Последний день месяца
                  ).replace(day=1) - timedelta(days=1),
        target_amount=Decimal('40000.00'),
        user_id=user.id
    )
    db.session.add(budget)

    db.session.commit()

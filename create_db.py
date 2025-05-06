from flask import Flask
from models import db, User, Category, Budget, Transaction, CategoryType, BudgetPeriod
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetnik.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

db.init_app(app)

with app.app_context():
    try:
        # Создаем таблицы
        logger.info("Создание таблиц базы данных...")
        db.create_all()

        # Проверяем, есть ли уже пользователи
        if User.query.count() > 0:
            logger.info(
                "В базе данных уже есть пользователи, пропускаем создание тестовых данных")
            exit(0)

        # Создаем тестовых пользователей
        logger.info("Создание тестовых пользователей...")

        demo_user = User(
            username='demo',
            email='demo@example.com'
        )
        demo_user.set_password('demo123')

        test_user = User(
            username='test',
            email='test@example.com'
        )
        test_user.set_password('test123')

        db.session.add(demo_user)
        db.session.add(test_user)
        db.session.commit()

        logger.info(
            f"Создано 2 тестовых пользователя: {demo_user.username}, {test_user.username}")

        # Создаем категории для demo пользователя
        logger.info("Создание категорий для тестового пользователя...")

        # Категории доходов
        income_categories = [
            Category(name="Зарплата", type=CategoryType.INCOME,
                     user_id=demo_user.id),
            Category(name="Фриланс", type=CategoryType.INCOME,
                     user_id=demo_user.id),
            Category(name="Инвестиции", type=CategoryType.INCOME,
                     user_id=demo_user.id),
            Category(name="Подарки", type=CategoryType.INCOME,
                     user_id=demo_user.id)
        ]

        # Категории расходов
        expense_categories = [
            Category(name="Продукты", type=CategoryType.EXPENSE,
                     user_id=demo_user.id),
            Category(name="Транспорт", type=CategoryType.EXPENSE,
                     user_id=demo_user.id),
            Category(name="Жилье", type=CategoryType.EXPENSE,
                     user_id=demo_user.id),
            Category(name="Развлечения", type=CategoryType.EXPENSE,
                     user_id=demo_user.id),
            Category(name="Здоровье", type=CategoryType.EXPENSE,
                     user_id=demo_user.id),
            Category(name="Одежда", type=CategoryType.EXPENSE,
                     user_id=demo_user.id)
        ]

        for category in income_categories + expense_categories:
            db.session.add(category)

        db.session.commit()
        logger.info(
            f"Создано {len(income_categories)} категорий доходов и {len(expense_categories)} категорий расходов")

        # Создаем бюджет на текущий месяц
        logger.info("Создание тестового бюджета...")

        today = date.today()
        # Первый день текущего месяца
        start_date = date(today.year, today.month, 1)

        # Последний день текущего месяца
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

        monthly_budget = Budget(
            name="Бюджет на текущий месяц",
            period=BudgetPeriod.MONTHLY,
            start_date=start_date,
            end_date=end_date,
            target_amount=Decimal('50000.00'),  # Цель на расходы
            user_id=demo_user.id
        )

        db.session.add(monthly_budget)
        db.session.commit()
        logger.info(
            f"Создан бюджет: {monthly_budget.name} ({start_date} - {end_date})")

        # Создаем тестовые транзакции
        logger.info("Создание тестовых транзакций...")

        # Доходы
        salary = Transaction(
            description="Зарплата за месяц",
            amount=Decimal('70000.00'),
            date=date.today() - timedelta(days=15),
            type=CategoryType.INCOME,
            category_id=income_categories[0].id,  # Зарплата
            user_id=demo_user.id
        )

        freelance = Transaction(
            description="Оплата за разработку сайта",
            amount=Decimal('15000.00'),
            date=date.today() - timedelta(days=5),
            type=CategoryType.INCOME,
            category_id=income_categories[1].id,  # Фриланс
            user_id=demo_user.id
        )

        # Расходы
        groceries1 = Transaction(
            description="Продукты в супермаркете",
            amount=Decimal('3500.00'),
            date=date.today() - timedelta(days=10),
            type=CategoryType.EXPENSE,
            category_id=expense_categories[0].id,  # Продукты
            user_id=demo_user.id
        )

        groceries2 = Transaction(
            description="Покупка продуктов",
            amount=Decimal('2800.00'),
            date=date.today() - timedelta(days=3),
            type=CategoryType.EXPENSE,
            category_id=expense_categories[0].id,  # Продукты
            user_id=demo_user.id
        )

        rent = Transaction(
            description="Аренда квартиры",
            amount=Decimal('25000.00'),
            date=date.today() - timedelta(days=12),
            type=CategoryType.EXPENSE,
            category_id=expense_categories[2].id,  # Жилье
            user_id=demo_user.id
        )

        entertainment = Transaction(
            description="Поход в кино",
            amount=Decimal('1200.00'),
            date=date.today() - timedelta(days=2),
            type=CategoryType.EXPENSE,
            category_id=expense_categories[3].id,  # Развлечения
            user_id=demo_user.id
        )

        transport = Transaction(
            description="Проездной на месяц",
            amount=Decimal('2000.00'),
            date=date.today() - timedelta(days=20),
            type=CategoryType.EXPENSE,
            category_id=expense_categories[1].id,  # Транспорт
            user_id=demo_user.id
        )

        transactions = [salary, freelance, groceries1,
                        groceries2, rent, entertainment, transport]
        for transaction in transactions:
            db.session.add(transaction)

        db.session.commit()
        logger.info(f"Создано {len(transactions)} тестовых транзакций")

        logger.info("Инициализация базы данных завершена успешно!")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при инициализации базы данных: {str(e)}")

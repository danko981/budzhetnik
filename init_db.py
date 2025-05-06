#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для инициализации базы данных и создания начальных тестовых данных.
Использует Flask-SQLAlchemy и Flask-Migrate для работы с БД.
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from flask import Flask
from flask_migrate import Migrate

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('init_db')


def create_app():
    """Создает экземпляр Flask-приложения для инициализации БД"""
    app = Flask(__name__)

    # Конфигурация базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///budgetnik.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Инициализация БД и миграций
    from models import db
    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    return app


def init_database(app):
    """Инициализирует базу данных и создает начальные тестовые данные"""
    from models import User, Category, Budget, Transaction, CategoryType, BudgetPeriod
    from werkzeug.security import generate_password_hash

    with app.app_context():
        # Создание таблиц (если используем SQLite)
        db = app.extensions['sqlalchemy'].db
        logger.info("Создание таблиц базы данных...")
        db.create_all()

        # Проверка, есть ли уже пользователи
        if User.query.count() > 0:
            logger.info(
                "В базе данных уже есть пользователи, пропускаем создание тестовых данных")
            return

        logger.info("Создание тестовых пользователей...")

        # Создаем тестовых пользователей
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


def main():
    """Основная функция для запуска скрипта"""
    try:
        app = create_app()
        init_database(app)
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

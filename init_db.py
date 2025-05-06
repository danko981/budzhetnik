#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных и создания тестовых данных
"""
import os
from app import db, create_app
from models import User, Category, Budget, Transaction, CategoryType, BudgetPeriod
from datetime import date, timedelta
from decimal import Decimal
import random


def init_db():
    """Инициализирует базу данных и создает таблицы"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("База данных инициализирована. Таблицы созданы.")


def create_demo_data():
    """Создает демонстрационные данные для приложения"""
    app = create_app()
    with app.app_context():
        # Проверяем, есть ли уже пользователи
        if User.query.count() > 0:
            print("В базе данных уже есть пользователи. Пропускаем создание демо-данных.")
            return

        # Создаем демо-пользователя
        demo_user = User(username="demo", email="demo@example.com")
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()
        print(f"Создан демо-пользователь: {demo_user.username}")

        # Создаем категории доходов
        income_categories = [
            Category(name="Зарплата", type=CategoryType.INCOME, owner=demo_user),
            Category(name="Фриланс", type=CategoryType.INCOME, owner=demo_user),
            Category(name="Инвестиции",
                     type=CategoryType.INCOME, owner=demo_user),
            Category(name="Подарки", type=CategoryType.INCOME, owner=demo_user)
        ]

        # Создаем категории расходов
        expense_categories = [
            Category(name="Продукты", type=CategoryType.EXPENSE,
                     owner=demo_user),
            Category(name="Транспорт",
                     type=CategoryType.EXPENSE, owner=demo_user),
            Category(name="Развлечения",
                     type=CategoryType.EXPENSE, owner=demo_user),
            Category(name="Коммунальные услуги",
                     type=CategoryType.EXPENSE, owner=demo_user),
            Category(name="Здоровье", type=CategoryType.EXPENSE,
                     owner=demo_user),
            Category(name="Одежда", type=CategoryType.EXPENSE, owner=demo_user)
        ]

        # Добавляем категории в базу данных
        for category in income_categories + expense_categories:
            db.session.add(category)
        db.session.commit()
        print(
            f"Создано {len(income_categories)} категорий доходов и {len(expense_categories)} категорий расходов")

        # Создаем бюджет на текущий месяц
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month +
                                1, 1) - timedelta(days=1)

        monthly_budget = Budget(
            name="Бюджет на месяц",
            period=BudgetPeriod.MONTHLY,
            start_date=start_of_month,
            end_date=end_of_month,
            target_amount=Decimal("50000.00"),
            owner=demo_user
        )
        db.session.add(monthly_budget)
        db.session.commit()
        print(f"Создан месячный бюджет: {monthly_budget.name}")

        # Создаем несколько транзакций за последние 30 дней
        descriptions = {
            CategoryType.INCOME: {
                1: ["Зарплата за месяц", "Аванс", "Премия"],
                2: ["Оплата за проект", "Разовая работа", "Консультация"],
                3: ["Дивиденды", "Проценты по вкладу", "Доход от аренды"],
                4: ["Подарок на день рождения", "Возврат долга", "Подарок от родственников"]
            },
            CategoryType.EXPENSE: {
                5: ["Покупка продуктов", "Заказ еды", "Ужин в ресторане", "Обед"],
                6: ["Такси", "Бензин", "Проездной на месяц", "Ремонт авто"],
                7: ["Кино", "Концерт", "Выставка", "Боулинг", "Бар"],
                8: ["Оплата электричества", "Оплата интернета", "Оплата воды", "Квартплата"],
                9: ["Лекарства", "Визит к врачу", "Стоматолог", "Анализы"],
                10: ["Покупка одежды", "Обувь", "Аксессуары"]
            }
        }

        # Генерируем транзакции
        transactions = []
        for i in range(30):
            # Дата в пределах последних 30 дней
            transaction_date = today - timedelta(days=random.randint(0, 29))

            # Создаем доходы (с меньшей вероятностью, чем расходы)
            if random.random() < 0.3:  # 30% вероятность
                category = random.choice(income_categories)
                category_id = category.id
                desc_list = descriptions[CategoryType.INCOME].get(
                    category_id, ["Доход"])
                amount = Decimal(random.randint(5000, 50000))
            else:
                category = random.choice(expense_categories)
                category_id = category.id
                desc_list = descriptions[CategoryType.EXPENSE].get(
                    category_id, ["Расход"])
                amount = Decimal(random.randint(100, 3000))

            description = random.choice(desc_list)

            transaction = Transaction(
                description=description,
                amount=amount,
                date=transaction_date,
                category_id=category_id,
                owner=demo_user
            )
            transactions.append(transaction)

        # Добавляем транзакции в базу данных
        for transaction in transactions:
            db.session.add(transaction)
        db.session.commit()
        print(f"Создано {len(transactions)} транзакций")

        print("Демонстрационные данные успешно созданы!")


if __name__ == "__main__":
    init_db()
    create_demo_data()

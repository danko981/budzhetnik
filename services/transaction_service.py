from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import date
from decimal import Decimal
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc, asc, and_

from models import Transaction, Category, db, CategoryType
from services.base_service import BaseService
from services.category_service import CategoryService


class TransactionService(BaseService):
    """
    Сервис для работы с транзакциями (доходами и расходами).
    Наследует базовые методы от BaseService и дополняет их
    специфичной для транзакций логикой.
    """

    @staticmethod
    def get_user_transactions(
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        sort_by: str = 'date',
        sort_direction: str = 'desc',
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:
        """
        Получение транзакций пользователя с фильтрацией и сортировкой.
        """
        try:
            query = Transaction.query.filter_by(user_id=user_id)

            # Применяем фильтры
            if start_date:
                query = query.filter(Transaction.date >= start_date)

            if end_date:
                query = query.filter(Transaction.date <= end_date)

            if category_id:
                query = query.filter(Transaction.category_id == category_id)

            if transaction_type:
                try:
                    type_enum = CategoryType(transaction_type)
                    query = query.filter(Transaction.type == type_enum)
                except ValueError:
                    return {"error": f"Неверный тип транзакции. Допустимые значения: {[t.value for t in CategoryType]}"}, 400

            # Применяем сортировку
            if sort_by not in ['date', 'amount', 'id']:
                sort_by = 'date'  # По умолчанию сортируем по дате

            sort_column = getattr(Transaction, sort_by)
            if sort_direction.lower() == 'asc':
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))

            # Применяем пагинацию
            total_count = query.count()
            transactions = query.limit(limit).offset(offset).all()

            # Форматируем результат
            result = [
                {
                    'id': transaction.id,
                    'description': transaction.description,
                    # Преобразуем Decimal в float для JSON
                    'amount': float(transaction.amount),
                    'date': transaction.date.isoformat(),
                    'type': transaction.type.value,
                    'category_id': transaction.category_id,
                    'category_name': transaction.category.name,
                    'user_id': transaction.user_id,
                    'created_at': transaction.created_at.isoformat() if transaction.created_at else None
                } for transaction in transactions
            ]

            return {
                'items': result,
                'total': total_count,
                'page': offset // limit + 1 if limit > 0 else 1,
                'pages': (total_count + limit - 1) // limit if limit > 0 else 1,
                'per_page': limit
            }, 200

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении транзакций пользователя: {str(e)}")
            return {"error": "Ошибка при получении транзакций"}, 500

    @staticmethod
    def create_transaction(user_id: int, data: Dict[str, Any]) -> Tuple[Union[Dict, Transaction], int]:
        """
        Создание новой транзакции.
        """
        try:
            # Проверяем наличие обязательных полей
            required_fields = ['amount', 'date', 'category_id']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Отсутствует обязательное поле: {field}"}, 400

            # Проверяем валидность суммы
            try:
                amount = Decimal(str(data['amount']))
                if amount <= 0:
                    return {"error": "Сумма должна быть положительной"}, 400
            except (ValueError, TypeError, decimal.InvalidOperation):
                return {"error": "Неверный формат суммы"}, 400

            # Проверяем валидность даты
            try:
                if isinstance(data['date'], str):
                    transaction_date = date.fromisoformat(data['date'])
                elif isinstance(data['date'], date):
                    transaction_date = data['date']
                else:
                    return {"error": "Неверный формат даты"}, 400
            except ValueError:
                return {"error": "Неверный формат даты. Используйте формат YYYY-MM-DD"}, 400

            # Проверяем, что категория существует и принадлежит пользователю
            category_id = data['category_id']
            category_result, status_code = CategoryService.get_category_with_check(
                category_id, user_id)

            if status_code != 200:
                return category_result, status_code

            category = category_result

            # Создаем транзакцию
            transaction = Transaction(
                description=data.get('description', ''),
                amount=amount,
                date=transaction_date,
                type=category.type,  # Устанавливаем тип в соответствии с категорией
                category_id=category_id,
                user_id=user_id
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'id': transaction.id,
                'description': transaction.description,
                'amount': float(transaction.amount),
                'date': transaction.date.isoformat(),
                'type': transaction.type.value,
                'category_id': transaction.category_id,
                'category_name': category.name,
                'user_id': transaction.user_id,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при создании транзакции: {str(e)}")
            return {"error": "Ошибка базы данных при создании транзакции"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при создании транзакции: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def update_transaction(transaction_id: int, user_id: int, data: Dict[str, Any]) -> Tuple[Union[Dict, Transaction], int]:
        """
        Обновление существующей транзакции.
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return {"error": "Транзакция не найдена"}, 404

            if transaction.user_id != user_id:
                return {"error": "У вас нет прав на редактирование этой транзакции"}, 403

            # Обновление суммы
            if 'amount' in data:
                try:
                    amount = Decimal(str(data['amount']))
                    if amount <= 0:
                        return {"error": "Сумма должна быть положительной"}, 400
                    transaction.amount = amount
                except (ValueError, TypeError, decimal.InvalidOperation):
                    return {"error": "Неверный формат суммы"}, 400

            # Обновление даты
            if 'date' in data:
                try:
                    if isinstance(data['date'], str):
                        transaction_date = date.fromisoformat(data['date'])
                    elif isinstance(data['date'], date):
                        transaction_date = data['date']
                    else:
                        return {"error": "Неверный формат даты"}, 400
                    transaction.date = transaction_date
                except ValueError:
                    return {"error": "Неверный формат даты. Используйте формат YYYY-MM-DD"}, 400

            # Обновление категории
            if 'category_id' in data:
                category_id = data['category_id']
                category_result, status_code = CategoryService.get_category_with_check(
                    category_id, user_id)

                if status_code != 200:
                    return category_result, status_code

                category = category_result
                transaction.category_id = category_id
                transaction.type = category.type  # Устанавливаем тип в соответствии с категорией

            # Обновление описания
            if 'description' in data:
                transaction.description = data['description']

            db.session.commit()

            return {
                'id': transaction.id,
                'description': transaction.description,
                'amount': float(transaction.amount),
                'date': transaction.date.isoformat(),
                'type': transaction.type.value,
                'category_id': transaction.category_id,
                'category_name': transaction.category.name,
                'user_id': transaction.user_id,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при обновлении транзакции: {str(e)}")
            return {"error": "Ошибка базы данных при обновлении транзакции"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при обновлении транзакции: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def delete_transaction(transaction_id: int, user_id: int) -> Tuple[Dict[str, str], int]:
        """
        Удаление транзакции.
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return {"error": "Транзакция не найдена"}, 404

            if transaction.user_id != user_id:
                return {"error": "У вас нет прав на удаление этой транзакции"}, 403

            db.session.delete(transaction)
            db.session.commit()

            return {"message": "Транзакция успешно удалена"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при удалении транзакции: {str(e)}")
            return {"error": "Ошибка базы данных при удалении транзакции"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при удалении транзакции: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def get_transaction_statistics(
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = 'category'
    ) -> Tuple[Dict, int]:
        """
        Получение статистики по транзакциям пользователя.
        """
        try:
            # Формируем базовые запросы для доходов и расходов
            income_query = Transaction.query.filter_by(
                user_id=user_id,
                type=CategoryType.INCOME
            )
            expense_query = Transaction.query.filter_by(
                user_id=user_id,
                type=CategoryType.EXPENSE
            )

            # Применяем фильтры по датам
            if start_date:
                income_query = income_query.filter(
                    Transaction.date >= start_date)
                expense_query = expense_query.filter(
                    Transaction.date >= start_date)

            if end_date:
                income_query = income_query.filter(
                    Transaction.date <= end_date)
                expense_query = expense_query.filter(
                    Transaction.date <= end_date)

            # Рассчитываем общие суммы
            total_income = db.session.query(func.sum(Transaction.amount)).select_from(
                income_query.subquery()).scalar() or 0
            total_expense = db.session.query(func.sum(Transaction.amount)).select_from(
                expense_query.subquery()).scalar() or 0

            # Группировка данных
            income_data = []
            expense_data = []

            if group_by == 'category':
                # Группировка по категориям
                income_by_category = db.session.query(
                    Category.name,
                    func.sum(Transaction.amount).label('total')
                ).join(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.type == CategoryType.INCOME
                )

                if start_date:
                    income_by_category = income_by_category.filter(
                        Transaction.date >= start_date)
                if end_date:
                    income_by_category = income_by_category.filter(
                        Transaction.date <= end_date)

                income_by_category = income_by_category.group_by(
                    Category.name).all()

                expense_by_category = db.session.query(
                    Category.name,
                    func.sum(Transaction.amount).label('total')
                ).join(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.type == CategoryType.EXPENSE
                )

                if start_date:
                    expense_by_category = expense_by_category.filter(
                        Transaction.date >= start_date)
                if end_date:
                    expense_by_category = expense_by_category.filter(
                        Transaction.date <= end_date)

                expense_by_category = expense_by_category.group_by(
                    Category.name).all()

                # Форматируем результаты
                income_data = [
                    {'name': name, 'amount': float(total), 'percentage': round(
                        float(total) / float(total_income) * 100, 2) if total_income else 0}
                    for name, total in income_by_category
                ]

                expense_data = [
                    {'name': name, 'amount': float(total), 'percentage': round(
                        float(total) / float(total_expense) * 100, 2) if total_expense else 0}
                    for name, total in expense_by_category
                ]

            elif group_by == 'date':
                # Здесь можно реализовать группировку по датам (например, по месяцам или неделям)
                # В этом примере опустим для краткости
                pass

            return {
                'total_income': float(total_income),
                'total_expense': float(total_expense),
                'balance': float(total_income - total_expense),
                'income_breakdown': income_data,
                'expense_breakdown': expense_data,
                'period': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                }
            }, 200

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении статистики: {str(e)}")
            return {"error": "Ошибка при получении статистики по транзакциям"}, 500

from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_

from models import Budget, Transaction, db, BudgetPeriod, CategoryType
from services.base_service import BaseService


class BudgetService(BaseService):
    """
    Сервис для работы с бюджетами.
    Наследует базовые методы от BaseService и дополняет их
    специфичной для бюджетов логикой.
    """

    @staticmethod
    def get_user_budgets(
        user_id: int,
        active_only: bool = False,
        period_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[Dict, int]:
        """
        Получение всех бюджетов пользователя с возможной фильтрацией.
        """
        try:
            query = Budget.query.filter_by(user_id=user_id)

            # Фильтрация только активных бюджетов
            if active_only:
                current_date = date.today()
                query = query.filter(and_(
                    Budget.start_date <= current_date,
                    Budget.end_date >= current_date
                ))

            # Фильтрация по типу периода
            if period_type:
                try:
                    period_enum = BudgetPeriod(period_type)
                    query = query.filter(Budget.period == period_enum)
                except ValueError:
                    return {"error": f"Неверный тип периода. Допустимые значения: {[p.value for p in BudgetPeriod]}"}, 400

            # Получаем общее количество
            total_count = query.count()

            # Применяем пагинацию
            budgets = query.order_by(Budget.start_date.desc()).limit(
                limit).offset(offset).all()

            # Формируем ответ с данными бюджетов
            result = []
            for budget in budgets:
                # Рассчитываем текущее состояние бюджета (выполнение плана)
                budget_data = {
                    'id': budget.id,
                    'name': budget.name,
                    'period': budget.period.value,
                    'start_date': budget.start_date.isoformat(),
                    'end_date': budget.end_date.isoformat(),
                    'target_amount': float(budget.target_amount) if budget.target_amount else None,
                    'user_id': budget.user_id,
                    'created_at': budget.created_at.isoformat() if budget.created_at else None
                }

                # Добавляем статистику по бюджету
                income, expense, balance = BudgetService._calculate_budget_stats(
                    user_id, budget.start_date, budget.end_date
                )

                budget_data['statistics'] = {
                    'income': float(income),
                    'expense': float(expense),
                    'balance': float(balance)
                }

                # Если есть целевая сумма, считаем процент выполнения
                if budget.target_amount:
                    remaining = float(budget.target_amount) - float(expense)
                    percentage = round(
                        (float(expense) / float(budget.target_amount)) * 100, 2)
                    budget_data['progress'] = {
                        'percentage': percentage,
                        'remaining': remaining
                    }

                result.append(budget_data)

            return {
                'items': result,
                'total': total_count,
                'page': offset // limit + 1 if limit > 0 else 1,
                'pages': (total_count + limit - 1) // limit if limit > 0 else 1,
                'per_page': limit
            }, 200

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении бюджетов пользователя: {str(e)}")
            return {"error": "Ошибка при получении бюджетов"}, 500

    @staticmethod
    def create_budget(user_id: int, data: Dict[str, Any]) -> Tuple[Union[Dict, Budget], int]:
        """
        Создание нового бюджета.
        """
        try:
            # Проверяем наличие обязательных полей
            required_fields = ['name', 'period', 'start_date', 'end_date']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Отсутствует обязательное поле: {field}"}, 400

            # Проверяем корректность периода
            try:
                period_enum = BudgetPeriod(data['period'])
            except ValueError:
                return {"error": f"Неверный тип периода. Допустимые значения: {[p.value for p in BudgetPeriod]}"}, 400

            # Проверяем корректность дат
            try:
                if isinstance(data['start_date'], str):
                    start_date = date.fromisoformat(data['start_date'])
                elif isinstance(data['start_date'], date):
                    start_date = data['start_date']
                else:
                    return {"error": "Неверный формат начальной даты"}, 400

                if isinstance(data['end_date'], str):
                    end_date = date.fromisoformat(data['end_date'])
                elif isinstance(data['end_date'], date):
                    end_date = data['end_date']
                else:
                    return {"error": "Неверный формат конечной даты"}, 400
            except ValueError:
                return {"error": "Неверный формат даты. Используйте формат YYYY-MM-DD"}, 400

            # Проверяем логику дат
            if end_date < start_date:
                return {"error": "Конечная дата не может быть раньше начальной"}, 400

            # Проверяем целевую сумму, если она указана
            target_amount = None
            if 'target_amount' in data and data['target_amount'] is not None:
                try:
                    target_amount = Decimal(str(data['target_amount']))
                    if target_amount <= 0:
                        return {"error": "Целевая сумма должна быть положительной"}, 400
                except (ValueError, TypeError, decimal.InvalidOperation):
                    return {"error": "Неверный формат целевой суммы"}, 400

            # Создаем новый бюджет
            budget = Budget(
                name=data['name'],
                period=period_enum,
                start_date=start_date,
                end_date=end_date,
                target_amount=target_amount,
                user_id=user_id
            )

            db.session.add(budget)
            db.session.commit()

            # Формируем ответ
            result = {
                'id': budget.id,
                'name': budget.name,
                'period': budget.period.value,
                'start_date': budget.start_date.isoformat(),
                'end_date': budget.end_date.isoformat(),
                'target_amount': float(budget.target_amount) if budget.target_amount else None,
                'user_id': budget.user_id,
                'created_at': budget.created_at.isoformat() if budget.created_at else None
            }

            return result, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при создании бюджета: {str(e)}")
            return {"error": "Ошибка базы данных при создании бюджета"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при создании бюджета: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def update_budget(budget_id: int, user_id: int, data: Dict[str, Any]) -> Tuple[Union[Dict, Budget], int]:
        """
        Обновление существующего бюджета.
        """
        try:
            budget = Budget.query.get(budget_id)

            if not budget:
                return {"error": "Бюджет не найден"}, 404

            if budget.user_id != user_id:
                return {"error": "У вас нет прав на редактирование этого бюджета"}, 403

            # Обновляем поля, которые переданы
            if 'name' in data:
                budget.name = data['name']

            if 'period' in data:
                try:
                    budget.period = BudgetPeriod(data['period'])
                except ValueError:
                    return {"error": f"Неверный тип периода. Допустимые значения: {[p.value for p in BudgetPeriod]}"}, 400

            # Обновляем даты, если они переданы
            if 'start_date' in data:
                try:
                    if isinstance(data['start_date'], str):
                        start_date = date.fromisoformat(data['start_date'])
                    elif isinstance(data['start_date'], date):
                        start_date = data['start_date']
                    else:
                        return {"error": "Неверный формат начальной даты"}, 400
                    budget.start_date = start_date
                except ValueError:
                    return {"error": "Неверный формат начальной даты. Используйте формат YYYY-MM-DD"}, 400

            if 'end_date' in data:
                try:
                    if isinstance(data['end_date'], str):
                        end_date = date.fromisoformat(data['end_date'])
                    elif isinstance(data['end_date'], date):
                        end_date = data['end_date']
                    else:
                        return {"error": "Неверный формат конечной даты"}, 400
                    budget.end_date = end_date
                except ValueError:
                    return {"error": "Неверный формат конечной даты. Используйте формат YYYY-MM-DD"}, 400

            # Проверяем логику дат после обновления
            if budget.end_date < budget.start_date:
                return {"error": "Конечная дата не может быть раньше начальной"}, 400

            # Обновляем целевую сумму, если она передана
            if 'target_amount' in data:
                if data['target_amount'] is None:
                    budget.target_amount = None
                else:
                    try:
                        target_amount = Decimal(str(data['target_amount']))
                        if target_amount <= 0:
                            return {"error": "Целевая сумма должна быть положительной"}, 400
                        budget.target_amount = target_amount
                    except (ValueError, TypeError, decimal.InvalidOperation):
                        return {"error": "Неверный формат целевой суммы"}, 400

            db.session.commit()

            # Рассчитываем статистику
            income, expense, balance = BudgetService._calculate_budget_stats(
                user_id, budget.start_date, budget.end_date
            )

            # Формируем ответ
            result = {
                'id': budget.id,
                'name': budget.name,
                'period': budget.period.value,
                'start_date': budget.start_date.isoformat(),
                'end_date': budget.end_date.isoformat(),
                'target_amount': float(budget.target_amount) if budget.target_amount else None,
                'user_id': budget.user_id,
                'created_at': budget.created_at.isoformat() if budget.created_at else None,
                'statistics': {
                    'income': float(income),
                    'expense': float(expense),
                    'balance': float(balance)
                }
            }

            # Добавляем прогресс, если есть целевая сумма
            if budget.target_amount:
                remaining = float(budget.target_amount) - float(expense)
                percentage = round(
                    (float(expense) / float(budget.target_amount)) * 100, 2)
                result['progress'] = {
                    'percentage': percentage,
                    'remaining': remaining
                }

            return result, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при обновлении бюджета: {str(e)}")
            return {"error": "Ошибка базы данных при обновлении бюджета"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при обновлении бюджета: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def delete_budget(budget_id: int, user_id: int) -> Tuple[Dict[str, str], int]:
        """
        Удаление бюджета.
        """
        try:
            budget = Budget.query.get(budget_id)

            if not budget:
                return {"error": "Бюджет не найден"}, 404

            if budget.user_id != user_id:
                return {"error": "У вас нет прав на удаление этого бюджета"}, 403

            db.session.delete(budget)
            db.session.commit()

            return {"message": "Бюджет успешно удален"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при удалении бюджета: {str(e)}")
            return {"error": "Ошибка базы данных при удалении бюджета"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при удалении бюджета: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def get_budget_details(budget_id: int, user_id: int) -> Tuple[Dict, int]:
        """
        Получение подробной информации о бюджете с текущей статистикой.
        """
        try:
            budget = Budget.query.get(budget_id)

            if not budget:
                return {"error": "Бюджет не найден"}, 404

            if budget.user_id != user_id:
                return {"error": "У вас нет прав на просмотр этого бюджета"}, 403

            # Рассчитываем статистику
            income, expense, balance = BudgetService._calculate_budget_stats(
                user_id, budget.start_date, budget.end_date
            )

            # Формируем подробный ответ
            result = {
                'id': budget.id,
                'name': budget.name,
                'period': budget.period.value,
                'start_date': budget.start_date.isoformat(),
                'end_date': budget.end_date.isoformat(),
                'target_amount': float(budget.target_amount) if budget.target_amount else None,
                'user_id': budget.user_id,
                'created_at': budget.created_at.isoformat() if budget.created_at else None,
                'statistics': {
                    'income': float(income),
                    'expense': float(expense),
                    'balance': float(balance)
                }
            }

            # Добавляем прогресс выполнения, если есть целевая сумма
            if budget.target_amount:
                remaining = float(budget.target_amount) - float(expense)
                percentage = round(
                    (float(expense) / float(budget.target_amount)) * 100, 2)
                result['progress'] = {
                    'percentage': percentage,
                    'remaining': remaining
                }

            # Добавляем информацию о статусе бюджета
            current_date = date.today()
            if current_date < budget.start_date:
                status = 'upcoming'
            elif current_date > budget.end_date:
                status = 'completed'
            else:
                status = 'active'

            result['status'] = status

            # Добавляем прогноз расходов на оставшийся период, если бюджет активный
            if status == 'active':
                total_days = (budget.end_date - budget.start_date).days + 1
                elapsed_days = (current_date - budget.start_date).days + 1
                remaining_days = (budget.end_date - current_date).days

                if elapsed_days > 0:
                    daily_expense = float(expense) / elapsed_days
                    projected_expense = float(
                        expense) + (daily_expense * remaining_days)

                    result['projection'] = {
                        'daily_expense': round(daily_expense, 2),
                        'projected_total': round(projected_expense, 2),
                        'elapsed_days': elapsed_days,
                        'remaining_days': remaining_days,
                        'total_days': total_days
                    }

                    # Если есть целевая сумма, добавляем проекцию выполнения
                    if budget.target_amount:
                        projected_remaining = float(
                            budget.target_amount) - projected_expense
                        projected_percentage = round(
                            (projected_expense / float(budget.target_amount)) * 100, 2)
                        result['projection']['target_remaining'] = round(
                            projected_remaining, 2)
                        result['projection']['target_percentage'] = projected_percentage

            return result, 200

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении деталей бюджета: {str(e)}")
            return {"error": "Ошибка при получении деталей бюджета"}, 500

    @staticmethod
    def _calculate_budget_stats(user_id: int, start_date: date, end_date: date) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Вспомогательный метод для расчета статистики бюджета.
        Возвращает общий доход, расход и баланс за период.
        """
        # Запрос для суммы доходов
        income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == CategoryType.INCOME,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or Decimal('0.00')

        # Запрос для суммы расходов
        expense = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == CategoryType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or Decimal('0.00')

        # Рассчитываем баланс
        balance = income - expense

        return income, expense, balance

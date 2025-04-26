import logging
# jsonify все еще нужен для кастомной структуры
from flask import request, current_app, jsonify
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import func, and_
from datetime import date, timedelta
from decimal import Decimal

from ..models import Transaction, Category, CategoryType
from .. import db

# Создаем Namespace
ns = Namespace('reports', description='Отчеты и аналитика по бюджету')

# --- Модели данных для Swagger ---
# Модель для элемента в разбивке расходов
expense_breakdown_model = ns.model('ExpenseBreakdown', {
    'category_id': fields.Integer(),
    'category_name': fields.String(),
    'total_amount': fields.Price(decimals=2)
})

# Модель для ответа /summary
report_summary_model = ns.model('ReportSummary', {
    'start_date': fields.Date(description='Начало периода отчета'),
    'end_date': fields.Date(description='Конец периода отчета'),
    'total_income': fields.Price(decimals=2, description='Общий доход за период'),
    'total_expense': fields.Price(decimals=2, description='Общий расход за период'),
    'net_total': fields.Price(decimals=2, description='Чистый итог (доход - расход)'),
    'expenses_by_category': fields.List(fields.Nested(expense_breakdown_model), description='Разбивка расходов по категориям')
})

# --- Парсеры аргументов запроса ---
summary_parser = reqparse.RequestParser()
summary_parser.add_argument('start_date', type=inputs.date_from_iso8601,
                            help='Начало периода (YYYY-MM-DD)', location='args')
summary_parser.add_argument('end_date', type=inputs.date_from_iso8601,
                            help='Конец периода (YYYY-MM-DD)', location='args')

# Вспомогательная функция для дат по умолчанию


def get_default_date_range():
    today = date.today()
    start_of_month = today.replace(day=1)
    next_month = (start_of_month + timedelta(days=32)).replace(day=1)
    # Возвращаем инклюзивные даты
    return start_of_month, next_month - timedelta(days=1)

# --- Ресурсы ---


@ns.route('/summary')
class SummaryReport(Resource):
    """Сводный отчет по доходам и расходам."""

    @ns.doc('get_summary_report', security='Bearer Auth')
    @ns.expect(summary_parser)
    # Не используем marshal_with здесь, т.к. структура ответа сложная и формируется вручную
    # Но описываем возможный ответ для документации
    @ns.response(200, 'Успешный отчет', model=report_summary_model)
    @ns.response(400, 'Неверный формат даты или end_date < start_date')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def get(self):
        """Получить сводный отчет за период"""
        args = summary_parser.parse_args()
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Устанавливаем даты по умолчанию (текущий месяц), если не переданы
        if not start_date or not end_date:
            start_date, end_date = get_default_date_range()
        elif end_date < start_date:
            ns.abort(400, message="End date cannot be earlier than start date.")

        # Конечная дата для запросов (< end_date + 1)
        end_date_exclusive = end_date + timedelta(days=1)

        # Запрос для общих сумм
        summary_results = db.session.query(
            Transaction.type,
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date < end_date_exclusive
        ).group_by(Transaction.type).all()

        total_income = Decimal('0.00')
        total_expense = Decimal('0.00')
        for result_type, total_amount in summary_results:
            amount = total_amount or Decimal('0.00')
            if result_type == CategoryType.INCOME:
                total_income = amount
            elif result_type == CategoryType.EXPENSE:
                total_expense = amount

        # Запрос для разбивки расходов
        expenses_by_category_results = db.session.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.sum(Transaction.amount).label('total_amount')
        ).join(Category, Transaction.category_id == Category.id
               ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == CategoryType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date < end_date_exclusive
        ).group_by(Category.id, Category.name
                   ).order_by(func.sum(Transaction.amount).desc()).all()

        expenses_breakdown = [
            {"category_id": cat_id, "category_name": cat_name,
                "total_amount": str(amount or Decimal('0.00'))}
            for cat_id, cat_name, amount in expenses_by_category_results
        ]

        response_data = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": str(total_income),
            "total_expense": str(total_expense),
            "net_total": str(total_income - total_expense),
            "expenses_by_category": expenses_breakdown
        }
        # Используем jsonify, т.к. структура сложная и уже подготовлена
        return jsonify(response_data)

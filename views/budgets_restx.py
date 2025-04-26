import logging
from flask import request, current_app
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.exc import IntegrityError
from datetime import date
# Если используется Marshmallow для доп. валидации
from marshmallow import ValidationError

from ..models import Budget, BudgetPeriod
# Используем схему Marshmallow для валидации дат и других правил
from ..schemas import BudgetSchema
from .. import db

# Создаем Namespace
ns = Namespace('budgets', description='Операции с бюджетами')

# --- Модели данных для Swagger ---
budget_model = ns.model('Budget', {
    'id': fields.Integer(readonly=True, description='ID бюджета'),
    'name': fields.String(required=True, description='Название бюджета', example='Бюджет на Май'),
    'period': fields.String(required=True, description='Период бюджета', enum=[p.value for p in BudgetPeriod], example='monthly'),
    'start_date': fields.Date(required=True, description='Дата начала (YYYY-MM-DD)'),
    'end_date': fields.Date(required=True, description='Дата окончания (YYYY-MM-DD)'),
    'target_amount': fields.Price(description='Планируемая сумма (опционально)', decimals=2, example=50000.00),
    'created_at': fields.DateTime(readonly=True, dt_format='iso8601')
})

# Модель для создания/обновления
budget_input_model = ns.model('BudgetInput', {
    'name': fields.String(required=True, description='Название бюджета', example='Бюджет на Май'),
    'period': fields.String(required=True, description='Период бюджета', enum=[p.value for p in BudgetPeriod], example='monthly'),
    'start_date': fields.Date(required=True, description='Дата начала (YYYY-MM-DD)', example='2024-05-01'),
    'end_date': fields.Date(required=True, description='Дата окончания (YYYY-MM-DD)', example='2024-05-31'),
    'target_amount': fields.Price(description='Планируемая сумма (опционально)', decimals=2, min=0, example=50000.00)
})

# --- Парсеры аргументов запроса ---
budget_list_parser = reqparse.RequestParser(bundle_errors=True)
budget_list_parser.add_argument('period', type=str, choices=[
                                p.value for p in BudgetPeriod], help='Фильтр по периоду', location='args')
budget_list_parser.add_argument('active_date', type=inputs.date_from_iso8601,
                                # Используем встроенный тип date
                                help='Фильтр по активной дате (YYYY-MM-DD)', location='args')
budget_list_parser.add_argument('sort_by', type=str, choices=[
                                'name', 'period', 'start_date', 'end_date', 'created_at'], default='start_date', help='Поле для сортировки', location='args')
budget_list_parser.add_argument('sort_order', type=str, choices=[
                                'asc', 'desc'], default='desc', help='Порядок сортировки', location='args')

# --- Marshmallow схема для валидации ---
budget_validator = BudgetSchema()

# --- Ресурсы ---


@ns.route('')
class BudgetList(Resource):
    """Работа со списком бюджетов и создание новых."""

    @ns.doc('list_budgets', security='Bearer Auth')
    @ns.expect(budget_list_parser)
    @ns.marshal_list_with(budget_model)
    @ns.response(400, 'Ошибка в параметрах фильтрации/сортировки')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def get(self):
        """Список бюджетов пользователя"""
        args = budget_list_parser.parse_args()
        query = Budget.query.filter_by(owner=current_user)

        # Фильтры
        if args['period']:
            query = query.filter(Budget.period == BudgetPeriod(args['period']))
        if args['active_date']:
            # active_date уже преобразован в date парсером
            query = query.filter(
                Budget.start_date <= args['active_date'], Budget.end_date >= args['active_date'])

        # Сортировка
        sort_column = getattr(Budget, args['sort_by'], Budget.start_date)
        if args['sort_order'] == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        budgets = query.all()
        return budgets

    @ns.doc('create_budget', security='Bearer Auth')
    # Используем модель RESTx для базовой валидации
    @ns.expect(budget_input_model, validate=True)
    @ns.marshal_with(budget_model, code=201)
    @ns.response(400, 'Ошибка валидации данных (включая end_date < start_date)')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def post(self):
        """Создать бюджет"""
        data = ns.payload
        # Дополнительная валидация через Marshmallow (особенно для дат)
        try:
            validated_data = budget_validator.load(data)
        except ValidationError as err:
            ns.abort(400, message=err.messages)

        # Преобразуем период в Enum
        validated_data['period'] = BudgetPeriod(validated_data['period'])

        new_budget = Budget(**validated_data, owner=current_user)

        try:
            db.session.add(new_budget)
            db.session.commit()
            current_app.logger.info(
                f"Budget '{new_budget.name}' created by user {current_user.id}")
        # Ошибки валидации модели (маловероятно после Marshmallow, но возможно)
        except ValueError as e:
            db.session.rollback()
            ns.abort(400, message=str(e))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error creating budget for user {current_user.id}: {e}", exc_info=True)
            ns.abort(500, message="Could not create budget.")

        return new_budget, 201


@ns.route('/<int:budget_id>')
@ns.response(404, 'Бюджет не найден или доступ запрещен')
@ns.response(401, 'Требуется авторизация')
@ns.param('budget_id', 'Идентификатор бюджета')
class BudgetResource(Resource):
    """Чтение, обновление и удаление конкретного бюджета."""

    @ns.doc('get_budget', security='Bearer Auth')
    @ns.marshal_with(budget_model)
    @jwt_required()
    def get(self, budget_id):
        """Получить бюджет по ID"""
        budget = Budget.query.filter_by(id=budget_id, owner=current_user).first_or_404(
            description="Budget not found or access denied.")
        return budget

    @ns.doc('update_budget', security='Bearer Auth')
    # Можно использовать partial=True, если все поля необязательны
    @ns.expect(budget_input_model)
    @ns.marshal_with(budget_model)
    @ns.response(400, 'Ошибка валидации данных (включая end_date < start_date)')
    @jwt_required()
    def put(self, budget_id):
        """Обновить бюджет"""
        budget = Budget.query.filter_by(id=budget_id, owner=current_user).first_or_404(
            description="Budget not found or access denied.")
        data = ns.payload

        # Валидация через Marshmallow (partial=True для частичного обновления)
        try:
            # Убираем существующие значения дат, если они не переданы, чтобы Marshmallow не ругался
            payload_for_validation = data.copy()
            if 'start_date' not in payload_for_validation:
                payload_for_validation['start_date'] = budget.start_date.isoformat(
                )
            if 'end_date' not in payload_for_validation:
                payload_for_validation['end_date'] = budget.end_date.isoformat(
                )

            validated_data = budget_validator.load(
                payload_for_validation, partial=True)
        except ValidationError as err:
            ns.abort(400, message=err.messages)

        # Обновляем поля объекта бюджета
        for key, value in validated_data.items():
            if key == 'period':
                value = BudgetPeriod(value)  # Преобразуем в Enum
            # Модель должна сама преобразовать даты из строк/объектов date
            setattr(budget, key, value)

        try:
            db.session.commit()
            current_app.logger.info(
                f"Budget {budget_id} updated by user {current_user.id}")
        except ValueError as e:  # Ошибки валидации модели
            db.session.rollback()
            ns.abort(400, message=str(e))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating budget {budget_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not update budget.")

        return budget

    @ns.doc('delete_budget', security='Bearer Auth')
    @ns.response(204, 'Бюджет успешно удален')
    @jwt_required()
    def delete(self, budget_id):
        """Удалить бюджет"""
        budget = Budget.query.filter_by(id=budget_id, owner=current_user).first_or_404(
            description="Budget not found or access denied.")

        try:
            db.session.delete(budget)
            db.session.commit()
            current_app.logger.info(
                f"Budget {budget_id} deleted by user {current_user.id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error deleting budget {budget_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not delete budget.")

        return '', 204

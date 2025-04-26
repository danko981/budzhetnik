import logging
from flask import request, current_app
from flask_restx import Namespace, Resource, fields, inputs
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal, InvalidOperation
from datetime import date
from marshmallow import ValidationError

from ..services import calculator_service  # Импортируем сервис
from ..schemas import SavingsCalculatorSchema  # Импортируем схему для валидации
from ..utils.error_handlers import handle_validation_error, handle_value_error, handle_exception, log_operation

# Создаем Namespace
ns = Namespace('calculator', description='Финансовые калькуляторы')

# --- Модели данных для Swagger ---
savings_goal_input_model = ns.model('SavingsGoalInput', {
    'target_amount': fields.Price(required=True, description='Целевая сумма', min=0.01, example=10000.00),
    'target_date': fields.Date(required=True, description='Дата достижения цели (YYYY-MM-DD)', example='2025-12-31'),
    'current_savings': fields.Price(description='Текущие накопления (по умолчанию 0)', min=0, example=500.00, default=0.00)
})

savings_goal_output_model = ns.model('SavingsGoalOutput', {
    'target_amount': fields.Price(decimals=2),
    'current_savings': fields.Price(decimals=2),
    'target_date': fields.Date(),
    'amount_to_save': fields.Price(decimals=2),
    'months_remaining': fields.Integer(),
    'required_monthly_savings': fields.Price(decimals=2),
    'message': fields.String(description='Дополнительное сообщение (например, цель достигнута)')
})

# --- Ресурсы ---


@ns.route('/savings-goal')
class SavingsGoalCalculator(Resource):
    """Расчет ежемесячных сбережений для достижения цели."""

    @ns.doc('calculate_savings_goal', security='Bearer Auth')
    @ns.expect(savings_goal_input_model, validate=True)
    # marshal_with не используем, т.к. сервис возвращает готовый словарь
    @ns.response(200, 'Расчет выполнен успешно', model=savings_goal_output_model)
    @ns.response(400, 'Ошибка валидации входных данных или логики расчета')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def post(self):
        """Рассчитать необходимые сбережения"""
        user_id = get_jwt_identity()

        try:
            # Используем схему Marshmallow для валидации данных
            schema = SavingsCalculatorSchema()
            data = schema.load(ns.payload)

            # Логируем операцию
            log_operation(
                operation_type="calculate",
                resource_type="savings_goal",
                user_id=user_id,
                details={"target_amount": str(data['target_amount']),
                         "target_date": data['target_date'].isoformat()}
            )

            # Вызов сервиса с проверенными данными
            result = calculator_service.calculate_required_savings(
                target_amount=data['target_amount'],
                target_date=data['target_date'],
                current_savings=data.get('current_savings', Decimal('0.00'))
            )

            return result, 200
        except ValidationError as e:
            return handle_validation_error(e)
        except ValueError as e:
            # Ловим ошибки валидации из сервиса
            return handle_value_error(e, log_error=True, user_id=user_id)
        except Exception as e:
            handle_exception(e, "savings calculator", user_id)
            # Эта строка никогда не выполнится, так как handle_exception вызывает abort
            return None

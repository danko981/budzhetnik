import logging
from flask import request, current_app
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import func  # Для сортировки в GET запросе
from datetime import date
from decimal import Decimal
# Для отлова, если используется доп. валидация
from marshmallow import ValidationError

from ..models import Transaction, Category, CategoryType
# Импортируем схемы Marshmallow, они все еще полезны для валидации и иногда для сериализации
from ..schemas import TransactionSchema, CategorySchema
from .. import db

# Создаем Namespace
ns = Namespace(
    'transactions', description='Операции с транзакциями (доходы/расходы)')

# --- Модели данных для Swagger ---
# Модель категории (для вложенного отображения)
category_nested_model = ns.model('CategoryNested', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(readonly=True),
    'type': fields.String(enum=[e.value for e in CategoryType], readonly=True)
})

# Основная модель транзакции для вывода
transaction_model = ns.model('Transaction', {
    'id': fields.Integer(readonly=True, description='ID транзакции'),
    'description': fields.String(description='Описание'),
    # Используем Price для денег
    'amount': fields.Price(required=True, description='Сумма', decimals=2),
    'date': fields.Date(required=True, description='Дата транзакции (YYYY-MM-DD)'),
    'type': fields.String(enum=[e.value for e in CategoryType], readonly=True, description='Тип (доход/расход)'),
    'created_at': fields.DateTime(readonly=True, dt_format='iso8601'),
    # Вложенная модель
    'category': fields.Nested(category_nested_model, description='Связанная категория')
})

# Модель для создания/обновления транзакции
transaction_input_model = ns.model('TransactionInput', {
    'description': fields.String(description='Описание', example='Обед'),
    'amount': fields.Price(required=True, description='Сумма (> 0)', decimals=2, min=0.01, example=350.00),
    'date': fields.Date(required=True, description='Дата (YYYY-MM-DD)', example='2024-05-15'),
    'category_id': fields.Integer(required=True, description='ID категории', example=1)
})

# --- Парсеры аргументов запроса (для GET списка) ---
# bundle_errors=True собирает все ошибки парсинга
transaction_list_parser = reqparse.RequestParser(bundle_errors=True)
transaction_list_parser.add_argument('type', type=str, choices=[
                                     e.value for e in CategoryType], help='Фильтр по типу (income/expense)', location='args')
transaction_list_parser.add_argument(
    'category_id', type=int, help='Фильтр по ID категории', location='args')
transaction_list_parser.add_argument(
    'start_date', type=str, help='Начальная дата периода (YYYY-MM-DD)', location='args')
transaction_list_parser.add_argument(
    'end_date', type=str, help='Конечная дата периода (YYYY-MM-DD)', location='args')
transaction_list_parser.add_argument('sort_by', type=str, choices=[
                                     'date', 'amount', 'created_at'], default='date', help='Поле для сортировки', location='args')
transaction_list_parser.add_argument('sort_order', type=str, choices=[
                                     'asc', 'desc'], default='desc', help='Порядок сортировки', location='args')

# --- Marshmallow Схемы (для сложной валидации/сериализации) ---
transaction_load_validator = TransactionSchema(
    exclude=("id", "created_at", "type", "category", "user_id"))
# transaction_dump_schema = TransactionSchema() # Можно использовать для дампа, если модель RESTx не подходит

# --- Ресурсы ---


@ns.route('')
class TransactionList(Resource):
    """Работа со списком транзакций и создание новых."""

    @ns.doc('list_transactions', security='Bearer Auth')
    @ns.expect(transaction_list_parser)
    # Используем marshal_list_with и модель RESTx для ответа
    @ns.marshal_list_with(transaction_model)
    @ns.response(400, 'Ошибка в параметрах фильтрации/сортировки')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def get(self):
        """Список транзакций пользователя (с фильтрацией и сортировкой)"""
        args = transaction_list_parser.parse_args()
        query = Transaction.query.filter_by(owner=current_user)

        # Применение фильтров
        if args['type']:
            query = query.filter(Transaction.type ==
                                 CategoryType(args['type']))
        if args['category_id']:
            # Проверяем доступность категории для пользователя
            category = Category.query.filter_by(
                id=args['category_id'], owner=current_user).first()
            if category:
                query = query.filter(
                    Transaction.category_id == args['category_id'])
            else:
                return [], 200  # Возвращаем пустой список, если категория недоступна
        try:
            if args['start_date']:
                start_date = date.fromisoformat(args['start_date'])
                query = query.filter(Transaction.date >= start_date)
            if args['end_date']:
                end_date = date.fromisoformat(args['end_date'])
                query = query.filter(Transaction.date <= end_date)
        except ValueError:
            ns.abort(400, message="Invalid date format. Use YYYY-MM-DD.")

        # Применение сортировки
        sort_column = getattr(Transaction, args['sort_by'], Transaction.date)
        if args['sort_order'] == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        transactions = query.all()
        # RESTx автоматически сериализует с помощью transaction_model
        return transactions

    @ns.doc('create_transaction', security='Bearer Auth')
    @ns.expect(transaction_input_model, validate=True)
    @ns.marshal_with(transaction_model, code=201)
    @ns.response(404, 'Категория не найдена или недоступна')
    @ns.response(400, 'Ошибка валидации данных')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def post(self):
        """Создать транзакцию"""
        data = ns.payload
        category_id = data['category_id']

        # Проверка категории
        category = Category.query.filter_by(
            id=category_id, owner=current_user).first()
        if not category:
            ns.abort(
                404, message=f"Category with id {category_id} not found or access denied.")

        # Можно добавить валидацию через Marshmallow при необходимости
        # try:
        #     transaction_load_validator.load(data)
        # except ValidationError as err:
        #     ns.abort(400, message=err.messages)

        # Создаем транзакцию (тип установится в модели)
        new_transaction = Transaction(
            # Используем get для необязательных полей
            description=data.get('description'),
            amount=data['amount'],
            date=data['date'],
            category_id=category_id,
            owner=current_user
        )

        try:
            db.session.add(new_transaction)
            db.session.commit()
            current_app.logger.info(
                f"Transaction {new_transaction.id} created for user {current_user.id}")
        # Ловим ошибки валидации модели (например, тип категории)
        except ValueError as e:
            db.session.rollback()
            # Возвращаем сообщение валидатора модели
            ns.abort(400, message=str(e))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error creating transaction for user {current_user.id}: {e}", exc_info=True)
            ns.abort(500, message="Could not create transaction.")

        # Возвращаем созданный объект, RESTx сериализует
        return new_transaction, 201


@ns.route('/<int:transaction_id>')
@ns.response(404, 'Транзакция не найдена или доступ запрещен')
@ns.response(401, 'Требуется авторизация')
@ns.param('transaction_id', 'Идентификатор транзакции')
class TransactionResource(Resource):
    """Чтение, обновление и удаление конкретной транзакции."""

    @ns.doc('get_transaction', security='Bearer Auth')
    @ns.marshal_with(transaction_model)
    @jwt_required()
    def get(self, transaction_id):
        """Получить транзакцию по ID"""
        transaction = Transaction.query.filter_by(id=transaction_id, owner=current_user).first_or_404(
            description="Transaction not found or access denied.")
        return transaction

    @ns.doc('update_transaction', security='Bearer Auth')
    # Используем ту же модель для обновления
    @ns.expect(transaction_input_model)
    @ns.marshal_with(transaction_model)
    @ns.response(404, 'Транзакция или новая категория не найдена/недоступна')
    @ns.response(400, 'Ошибка валидации данных')
    @jwt_required()
    def put(self, transaction_id):
        """Обновить транзакцию"""
        transaction = Transaction.query.filter_by(id=transaction_id, owner=current_user).first_or_404(
            description="Transaction not found or access denied.")
        data = ns.payload

        # Опциональная валидация через Marshmallow
        # try:
        #     transaction_load_validator.load(data, partial=True)
        # except ValidationError as err:
        #     ns.abort(400, message=err.messages)

        # Проверка новой категории, если она меняется
        if 'category_id' in data and data['category_id'] != transaction.category_id:
            new_category_id = data['category_id']
            category = Category.query.filter_by(
                id=new_category_id, owner=current_user).first()
            if not category:
                ns.abort(
                    404, message=f"New category with id {new_category_id} not found or access denied.")
            # Валидатор модели проверит тип при присваивании

        # Обновляем поля объекта транзакции
        for key, value in data.items():
            # Преобразуем дату из строки, если она передана
            if key == 'date' and isinstance(value, str):
                try:
                    value = date.fromisoformat(value)
                except ValueError:
                    ns.abort(
                        400, message=f"Invalid date format for {key}. Use YYYY-MM-DD.")
            # Преобразуем сумму из строки/числа в Decimal
            if key == 'amount':
                try:
                    value = Decimal(value)
                    if value <= 0:
                        ns.abort(400, message="Amount must be positive.")
                except Exception:
                    ns.abort(400, message="Invalid amount format.")

            # Не позволяем напрямую менять 'type' через API
            if key != 'type':
                setattr(transaction, key, value)

        try:
            db.session.commit()
            current_app.logger.info(
                f"Transaction {transaction_id} updated by user {current_user.id}")
        except ValueError as e:  # Ловим ошибки валидации модели
            db.session.rollback()
            ns.abort(400, message=str(e))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating transaction {transaction_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not update transaction.")

        return transaction

    @ns.doc('delete_transaction', security='Bearer Auth')
    @ns.response(204, 'Транзакция успешно удалена')
    @jwt_required()
    def delete(self, transaction_id):
        """Удалить транзакцию"""
        transaction = Transaction.query.filter_by(id=transaction_id, owner=current_user).first_or_404(
            description="Transaction not found or access denied.")

        try:
            db.session.delete(transaction)
            db.session.commit()
            current_app.logger.info(
                f"Transaction {transaction_id} deleted by user {current_user.id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error deleting transaction {transaction_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not delete transaction.")

        return '', 204

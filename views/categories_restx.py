import logging
from flask import request, current_app
# Основные компоненты RESTx
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.exc import IntegrityError
# Импортируем для явного отлова, если нужно
from marshmallow import ValidationError

from ..models import Category, Transaction, CategoryType
# Marshmallow схема все еще полезна для валидации
from ..schemas import CategorySchema
from .. import db

# Создаем Namespace - аналог Blueprint для RESTx
ns = Namespace(
    'categories', description='Операции с категориями доходов и расходов')

# --- Модели данных для Swagger (описание входных/выходных данных) ---
# Используем `api.model` или `ns.model` для определения структуры
category_model = ns.model('Category', {
    'id': fields.Integer(readonly=True, description='Уникальный идентификатор категории'),
    'name': fields.String(required=True, description='Название категории', example='Продукты'),
    # Используем Enum поле Flask-RESTx
    'type': fields.String(required=True, description='Тип категории (доход/расход)', enum=[e.value for e in CategoryType], example='expense')
})

# Модель для создания категории (без id)
category_input_model = ns.model('CategoryInput', {
    'name': fields.String(required=True, description='Название категории', example='Продукты'),
    'type': fields.String(required=True, description='Тип категории (доход/расход)', enum=[e.value for e in CategoryType], example='expense')
})

# --- Парсеры аргументов запроса (для GET списка) ---
category_list_parser = reqparse.RequestParser()
category_list_parser.add_argument('type', type=str, choices=[
                                  e.value for e in CategoryType], help='Фильтр по типу категории (income/expense)', location='args')

# --- Marshmallow схемы (для валидации) ---
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

# --- Ресурсы (обработчики эндпоинтов) ---


@ns.route('')  # Маршрут для /api/v1/categories
class CategoryList(Resource):
    """Работа со списком категорий и создание новых."""

    @ns.doc('list_categories', description='Получение списка категорий текущего пользователя с фильтрацией по типу.')
    @ns.expect(category_list_parser)  # Описываем ожидаемые GET параметры
    # Описываем формат успешного ответа (список)
    @ns.marshal_list_with(category_model)
    @jwt_required()
    def get(self):
        """Список категорий пользователя"""
        args = category_list_parser.parse_args()  # Парсим GET аргументы
        query = Category.query.filter_by(owner=current_user)

        category_type_filter = args.get('type')
        if category_type_filter:
            # Преобразование строки в Enum безопасно, т.к. parser проверяет choices
            cat_type_enum = CategoryType(category_type_filter)
            query = query.filter_by(type=cat_type_enum)

        all_categories = query.order_by(Category.name).all()
        return all_categories  # Flask-RESTx автоматически сериализует с помощью category_model

    @ns.doc('create_category', description='Создание новой категории.')
    # Описываем ожидаемые POST данные и включаем валидацию
    @ns.expect(category_input_model, validate=True)
    # Описываем формат ответа при успехе (код 201)
    @ns.marshal_with(category_model, code=201)
    @ns.response(400, 'Ошибка валидации входных данных')
    @ns.response(409, 'Категория с таким именем и типом уже существует')
    @ns.response(401, 'Требуется авторизация')
    @jwt_required()
    def post(self):
        """Создать категорию"""
        # Используем ns.payload для доступа к валидированным данным
        data = ns.payload
        # Дополнительная валидация с Marshmallow (если нужна более сложная логика)
        # try:
        #     category_schema.load(data) # Проверяем через Marshmallow
        # except ValidationError as err:
        #     ns.abort(400, message=err.messages) # Используем ns.abort

        # Преобразуем тип из строки в Enum для модели
        try:
            data['type'] = CategoryType(data['type'])
        except ValueError:
            # Это не должно произойти из-за enum в модели RESTx, но на всякий случай
            ns.abort(400, message=f"Invalid category type specified.")

        new_category = Category(**data, owner=current_user)

        try:
            db.session.add(new_category)
            db.session.commit()
            current_app.logger.info(
                f"Category '{new_category.name}' created by user {current_user.id}")
        except IntegrityError:
            db.session.rollback()
            # Используем ns.abort для стандартных ошибок
            ns.abort(
                409, message=f"Category with name '{data['name']}' and type '{data['type'].value}' already exists for this user.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error creating category for user {current_user.id}: {e}", exc_info=True)
            ns.abort(500, message="Could not create category.")

        return new_category, 201  # Возвращаем объект SQLAlchemy, RESTx сериализует


@ns.route('/<int:category_id>')  # Маршрут для /api/v1/categories/{id}
@ns.response(404, 'Категория не найдена или доступ запрещен')
@ns.response(401, 'Требуется авторизация')
@ns.param('category_id', 'Идентификатор категории')  # Описание параметра пути
class CategoryResource(Resource):
    """Чтение, обновление и удаление конкретной категории."""

    @ns.doc('get_category', description='Получение данных одной категории по ID.')
    @ns.marshal_with(category_model)  # Описываем формат успешного ответа
    @jwt_required()
    def get(self, category_id):
        """Получить категорию по ID"""
        category = Category.query.filter_by(
            id=category_id, owner=current_user).first()
        if not category:
            ns.abort(404, message="Category not found or access denied.")
        return category

    @ns.doc('update_category', description='Обновление существующей категории.')
    # Ожидаем модель для ввода, но не все поля обязательны (PUT может быть частичным)
    # Можно определить другую модель для PUT, если нужно
    @ns.expect(category_input_model)
    @ns.marshal_with(category_model)  # Формат ответа
    @ns.response(409, 'Конфликт имени/типа или нельзя изменить тип с транзакциями')
    @ns.response(400, 'Ошибка валидации')
    @jwt_required()
    def put(self, category_id):
        """Обновить категорию"""
        category = Category.query.filter_by(id=category_id, owner=current_user).first_or_404(
            description="Category not found or access denied.")

        data = ns.payload
        # Опционально валидируем через Marshmallow
        # try:
        #     category_schema.load(data, partial=True)
        # except ValidationError as err:
        #     ns.abort(400, message=err.messages)

        # Обновляем поля, если они переданы
        original_type = category.type
        if 'name' in data:
            category.name = data['name']
        if 'type' in data:
            try:
                new_type = CategoryType(data['type'])
                if new_type != original_type:
                    # Проверка на наличие транзакций при смене типа
                    if category.transactions.first():
                        ns.abort(
                            409, message="Cannot change the type of a category that has associated transactions.")
                    category.type = new_type
            except ValueError:
                ns.abort(400, message="Invalid category type specified.")

        try:
            db.session.commit()
            current_app.logger.info(
                f"Category {category_id} updated by user {current_user.id}")
        except IntegrityError:
            db.session.rollback()
            ns.abort(
                409, message=f"Category name '{category.name}' with type '{category.type.value}' conflicts with an existing category.")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error updating category {category_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not update category.")

        return category

    @ns.doc('delete_category', description='Удаление категории.')
    @ns.response(204, 'Категория успешно удалена')
    @ns.response(409, 'Нельзя удалить категорию со связанными транзакциями')
    @jwt_required()
    def delete(self, category_id):
        """Удалить категорию"""
        category = Category.query.filter_by(id=category_id, owner=current_user).first_or_404(
            description="Category not found or access denied.")

        # Проверка на связанные транзакции
        if category.transactions.first():
            ns.abort(
                409, message="Cannot delete category with associated transactions. Please reassign or delete transactions first.")

        try:
            db.session.delete(category)
            db.session.commit()
            current_app.logger.info(
                f"Category {category_id} deleted by user {current_user.id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error deleting category {category_id}: {e}", exc_info=True)
            ns.abort(500, message="Could not delete category.")

        return '', 204

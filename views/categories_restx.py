import logging
from flask import request, current_app
# Основные компоненты RESTx
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity

from models import CategoryType
from services.category_service import CategoryService

# Создаем Namespace - аналог Blueprint для RESTx
ns = Namespace(
    'categories', description='Операции с категориями доходов и расходов')

# --- Модели данных для Swagger (описание входных/выходных данных) ---
category_model = ns.model('Category', {
    'id': fields.Integer(readonly=True, description='Уникальный идентификатор категории'),
    'name': fields.String(required=True, description='Название категории', example='Продукты'),
    'type': fields.String(required=True, description='Тип категории (доход/расход)', enum=[e.value for e in CategoryType], example='expense'),
    'user_id': fields.Integer(readonly=True, description='ID владельца категории')
})

# Модель для создания категории (без id)
category_input_model = ns.model('CategoryInput', {
    'name': fields.String(required=True, description='Название категории', example='Продукты'),
    'type': fields.String(required=True, description='Тип категории (доход/расход)', enum=[e.value for e in CategoryType], example='expense')
})

# Модель ответа с ошибкой
error_model = ns.model('Error', {
    'error': fields.String(required=True, description='Сообщение об ошибке')
})

# --- Парсеры аргументов запроса (для GET списка) ---
category_list_parser = reqparse.RequestParser()
category_list_parser.add_argument('type', type=str, choices=[
                                  e.value for e in CategoryType], help='Фильтр по типу категории (income/expense)', location='args')

# --- Ресурсы (обработчики эндпоинтов) ---


@ns.route('')  # Маршрут для /api/v1/categories
class CategoryList(Resource):
    """Работа со списком категорий и создание новых."""

    @ns.doc('list_categories', description='Получение списка категорий текущего пользователя с фильтрацией по типу.')
    @ns.expect(category_list_parser)  # Описываем ожидаемые GET параметры
    @ns.response(200, 'Успешно', [category_model])
    @ns.response(401, 'Требуется авторизация')
    @ns.response(500, 'Внутренняя ошибка сервера', error_model)
    @jwt_required()
    def get(self):
        """Список категорий пользователя"""
        try:
            user_id = get_jwt_identity()
            args = category_list_parser.parse_args()  # Парсим GET аргументы

            type_filter = None
            if args.get('type'):
                try:
                    type_filter = CategoryType(args.get('type'))
                except ValueError:
                    return {"error": f"Неверный тип категории"}, 400

            # Используем сервис для получения категорий
            result, status_code = CategoryService.get_user_categories(
                user_id, type_filter)
            return result, status_code

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении категорий: {str(e)}")
            return {"error": "Ошибка при получении категорий"}, 500

    @ns.doc('create_category', description='Создание новой категории.')
    @ns.expect(category_input_model, validate=True)
    @ns.response(201, 'Категория успешно создана', category_model)
    @ns.response(400, 'Ошибка валидации входных данных', error_model)
    @ns.response(401, 'Требуется авторизация')
    @ns.response(500, 'Внутренняя ошибка сервера', error_model)
    @jwt_required()
    def post(self):
        """Создать категорию"""
        try:
            user_id = get_jwt_identity()
            data = request.json

            if not data or not data.get('name') or not data.get('type'):
                return {"error": "Необходимо указать имя и тип категории"}, 400

            # Используем сервис для создания категории
            result, status_code = CategoryService.create_category(
                user_id=user_id,
                name=data['name'],
                category_type=data['type']
            )

            return result, status_code

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при создании категории: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500


@ns.route('/<int:category_id>')  # Маршрут для /api/v1/categories/{id}
@ns.response(404, 'Категория не найдена или доступ запрещен')
@ns.response(401, 'Требуется авторизация')
@ns.param('category_id', 'Идентификатор категории')  # Описание параметра пути
class CategoryResource(Resource):
    """Чтение, обновление и удаление конкретной категории."""

    @ns.doc('get_category', description='Получение данных одной категории по ID.')
    @ns.response(200, 'Успешно', category_model)
    @ns.response(403, 'Доступ запрещен', error_model)
    @jwt_required()
    def get(self, category_id):
        """Получить категорию по ID"""
        try:
            user_id = get_jwt_identity()

            # Используем сервис для получения категории с проверкой доступа
            category, status_code = CategoryService.get_category_with_check(
                category_id=category_id,
                user_id=user_id
            )

            if status_code != 200:
                return category, status_code

            # Преобразуем результат в словарь
            return {
                'id': category.id,
                'name': category.name,
                'type': category.type.value,
                'user_id': category.user_id
            }, 200

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении категории {category_id}: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @ns.doc('update_category', description='Обновление существующей категории.')
    @ns.expect(category_input_model)
    @ns.response(200, 'Категория успешно обновлена', category_model)
    @ns.response(400, 'Ошибка валидации', error_model)
    @ns.response(403, 'Доступ запрещен', error_model)
    @jwt_required()
    def put(self, category_id):
        """Обновить категорию"""
        try:
            user_id = get_jwt_identity()
            data = request.json

            if not data:
                return {"error": "Нет данных для обновления"}, 400

            # Используем сервис для обновления категории
            result, status_code = CategoryService.update_category(
                category_id=category_id,
                user_id=user_id,
                data=data
            )

            return result, status_code

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при обновлении категории {category_id}: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @ns.doc('delete_category', description='Удаление категории.')
    @ns.response(200, 'Категория успешно удалена')
    @ns.response(400, 'Нельзя удалить категорию со связанными транзакциями', error_model)
    @ns.response(403, 'Доступ запрещен', error_model)
    @jwt_required()
    def delete(self, category_id):
        """Удалить категорию"""
        try:
            user_id = get_jwt_identity()

            # Используем сервис для удаления категории
            result, status_code = CategoryService.delete_category(
                category_id=category_id,
                user_id=user_id
            )

            return result, status_code

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при удалении категории {category_id}: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

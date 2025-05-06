from typing import Dict, List, Optional, Tuple, Union, Any
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import current_user

from models import Category, db, CategoryType
from services.base_service import BaseService


class CategoryService(BaseService):
    """
    Сервис для работы с категориями доходов и расходов.
    Наследует базовые методы от BaseService и дополняет их
    специфичной для категорий логикой.
    """

    @staticmethod
    def get_user_categories(user_id: int, type_filter: Optional[CategoryType] = None) -> Tuple[List[Dict], int]:
        """
        Получение всех категорий пользователя с возможной фильтрацией по типу.
        """
        try:
            query = Category.query.filter_by(user_id=user_id)

            if type_filter:
                query = query.filter_by(type=type_filter)

            categories = query.all()
            result = [
                {
                    'id': category.id,
                    'name': category.name,
                    'type': category.type.value,
                    'user_id': category.user_id
                } for category in categories
            ]

            return result, 200
        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении категорий пользователя: {str(e)}")
            return {"error": "Ошибка при получении категорий"}, 500

    @staticmethod
    def create_category(user_id: int, name: str, category_type: str) -> Tuple[Union[Dict, Category], int]:
        """
        Создание новой категории для пользователя.
        """
        try:
            # Проверка уникальности имени категории для пользователя и типа
            try:
                # Преобразуем строковое представление типа в enum
                type_enum = CategoryType(category_type)
            except ValueError:
                return {"error": f"Неверный тип категории. Допустимые значения: {[t.value for t in CategoryType]}"}, 400

            existing = Category.query.filter_by(
                user_id=user_id,
                name=name,
                type=type_enum
            ).first()

            if existing:
                return {"error": f"Категория с именем '{name}' и типом '{category_type}' уже существует"}, 400

            # Создание новой категории
            category = Category(
                name=name,
                type=type_enum,
                user_id=user_id
            )

            db.session.add(category)
            db.session.commit()

            return {
                'id': category.id,
                'name': category.name,
                'type': category.type.value,
                'user_id': category.user_id
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при создании категории: {str(e)}")
            return {"error": "Ошибка базы данных при создании категории"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при создании категории: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def update_category(category_id: int, user_id: int, data: Dict[str, Any]) -> Tuple[Union[Dict, Category], int]:
        """
        Обновление существующей категории.
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                return {"error": "Категория не найдена"}, 404

            if category.user_id != user_id:
                return {"error": "У вас нет прав на редактирование этой категории"}, 403

            # Проверяем, не пытается ли пользователь установить имя, которое уже существует
            if 'name' in data:
                name = data['name']
                type_enum = category.type

                if 'type' in data:
                    try:
                        type_enum = CategoryType(data['type'])
                    except ValueError:
                        return {"error": f"Неверный тип категории. Допустимые значения: {[t.value for t in CategoryType]}"}, 400

                existing = Category.query.filter_by(
                    user_id=user_id,
                    name=name,
                    type=type_enum
                ).filter(Category.id != category_id).first()

                if existing:
                    return {"error": f"Категория с именем '{name}' и типом '{type_enum.value}' уже существует"}, 400

            # Обновляем данные
            if 'name' in data:
                category.name = data['name']

            if 'type' in data:
                try:
                    category.type = CategoryType(data['type'])
                except ValueError:
                    return {"error": f"Неверный тип категории. Допустимые значения: {[t.value for t in CategoryType]}"}, 400

            db.session.commit()

            return {
                'id': category.id,
                'name': category.name,
                'type': category.type.value,
                'user_id': category.user_id
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при обновлении категории: {str(e)}")
            return {"error": "Ошибка базы данных при обновлении категории"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при обновлении категории: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def delete_category(category_id: int, user_id: int) -> Tuple[Dict[str, str], int]:
        """
        Удаление категории.
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                return {"error": "Категория не найдена"}, 404

            if category.user_id != user_id:
                return {"error": "У вас нет прав на удаление этой категории"}, 403

            # Проверяем, есть ли транзакции, связанные с категорией
            if category.transactions.count() > 0:
                return {"error": "Категория не может быть удалена, так как с ней связаны транзакции"}, 400

            db.session.delete(category)
            db.session.commit()

            return {"message": "Категория успешно удалена"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при удалении категории: {str(e)}")
            return {"error": "Ошибка базы данных при удалении категории"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при удалении категории: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def get_category_with_check(category_id: int, user_id: int) -> Tuple[Union[Dict[str, str], Category], int]:
        """
        Получение категории с проверкой доступа.
        """
        category = Category.query.get(category_id)

        if not category:
            return {"error": "Категория не найдена"}, 404

        if category.user_id != user_id:
            return {"error": "У вас нет прав на доступ к этой категории"}, 403

        return category, 200

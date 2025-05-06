from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union
from models import db

T = TypeVar('T')


class BaseService:
    """
    Базовый сервис для работы с сущностями в базе данных.
    Содержит общие методы CRUD, которые могут быть наследованы 
    и переопределены в других сервисах.
    """

    @staticmethod
    def get_by_id(model: Type[T], id: int) -> Optional[T]:
        """Получение сущности по ID"""
        return model.query.get(id)

    @staticmethod
    def get_all(model: Type[T], filters: Dict = None, limit: int = None) -> List[T]:
        """Получение всех сущностей с опциональной фильтрацией"""
        query = model.query

        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def create(model: Type[T], data: Dict[str, Any]) -> Tuple[Union[T, Dict[str, str]], int]:
        """Создание новой сущности"""
        try:
            entity = model(**data)
            db.session.add(entity)
            db.session.commit()
            return entity, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при создании {model.__name__}: {str(e)}")
            return {"error": f"Ошибка базы данных при создании {model.__name__}"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при создании {model.__name__}: {str(e)}")
            return {"error": f"Внутренняя ошибка сервера при создании {model.__name__}"}, 500

    @staticmethod
    def update(entity: T, data: Dict[str, Any]) -> Tuple[Union[T, Dict[str, str]], int]:
        """Обновление существующей сущности"""
        try:
            # Обновляем только те поля, которые переданы в data
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            db.session.commit()
            return entity, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при обновлении {type(entity).__name__}: {str(e)}")
            return {"error": f"Ошибка базы данных при обновлении {type(entity).__name__}"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при обновлении {type(entity).__name__}: {str(e)}")
            return {"error": f"Внутренняя ошибка сервера при обновлении {type(entity).__name__}"}, 500

    @staticmethod
    def delete(entity: T) -> Tuple[Dict[str, str], int]:
        """Удаление сущности"""
        try:
            entity_name = type(entity).__name__
            db.session.delete(entity)
            db.session.commit()
            return {"message": f"{entity_name} успешно удален"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при удалении {type(entity).__name__}: {str(e)}")
            return {"error": f"Ошибка базы данных при удалении {type(entity).__name__}"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при удалении {type(entity).__name__}: {str(e)}")
            return {"error": f"Внутренняя ошибка сервера при удалении {type(entity).__name__}"}, 500

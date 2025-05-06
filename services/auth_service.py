from flask import current_app
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token

from models import User, db


class AuthService:
    """
    Сервис для управления аутентификацией пользователей.
    Использует современные практики безопасности и работает с базой данных.
    """

    @staticmethod
    def register_user(username, email, password):
        """
        Регистрирует нового пользователя.
        Возвращает токен доступа и пользовательские данные в случае успеха.
        """
        try:
            # Проверка существования пользователя
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                if existing_user.username == username:
                    return {"error": "Пользователь с таким именем уже существует"}, 400
                return {"error": "Email уже используется"}, 400

            # Создание нового пользователя
            new_user = User(username=username, email=email)
            new_user.set_password(password)

            # Сохранение в базе данных
            db.session.add(new_user)
            db.session.commit()

            # Создание токенов
            access_token = create_access_token(identity=new_user)
            refresh_token = create_refresh_token(identity=new_user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email
                },
                "message": "Пользователь успешно зарегистрирован"
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при регистрации: {str(e)}")
            return {"error": "Ошибка базы данных при регистрации"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при регистрации: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def login_user(username, password):
        """
        Аутентифицирует пользователя.
        Возвращает токен доступа и пользовательские данные в случае успеха.
        """
        try:
            # Находим пользователя
            user = User.query.filter_by(username=username).first()

            # Проверяем существование пользователя и корректность пароля
            if not user or not user.check_password(password):
                return {"error": "Неверное имя пользователя или пароль"}, 401

            # Создаем токены
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "message": "Авторизация успешна"
            }, 200

        except SQLAlchemyError as e:
            current_app.logger.error(
                f"Ошибка SQLAlchemy при авторизации: {str(e)}")
            return {"error": "Ошибка базы данных при авторизации"}, 500
        except Exception as e:
            current_app.logger.error(
                f"Неожиданная ошибка при авторизации: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

    @staticmethod
    def refresh_token(user):
        """
        Обновляет токен доступа на основе refresh token.
        """
        try:
            access_token = create_access_token(identity=user)
            return {"access_token": access_token}, 200
        except Exception as e:
            current_app.logger.error(f"Ошибка при обновлении токена: {str(e)}")
            return {"error": "Ошибка при обновлении токена"}, 500

    @staticmethod
    def update_user(user_id, data):
        """
        Обновляет данные пользователя.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "Пользователь не найден"}, 404

            # Обновляем только разрешенные поля
            if 'email' in data:
                # Проверка уникальности email
                existing = User.query.filter(
                    User.email == data['email'], User.id != user_id).first()
                if existing:
                    return {"error": "Email уже используется другим пользователем"}, 400
                user.email = data['email']

            if 'password' in data:
                user.set_password(data['password'])

            db.session.commit()

            return {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "message": "Данные пользователя обновлены"
            }, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(
                f"Ошибка SQLAlchemy при обновлении пользователя: {str(e)}")
            return {"error": "Ошибка базы данных при обновлении"}, 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Неожиданная ошибка при обновлении пользователя: {str(e)}")
            return {"error": "Внутренняя ошибка сервера"}, 500

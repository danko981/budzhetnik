from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
import jwt
import datetime
import os
import json
import logging

# Создаем Namespace для авторизации
ns = Namespace('auth', description='Операции с аутентификацией и авторизацией')

# Путь к файлу хранения пользователей
USERS_FILE = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'users.json')

# Проверяем наличие директории для данных
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# Определение моделей данных для API документации
user_model = ns.model('User', {
    'id': fields.Integer(readonly=True, description='ID пользователя'),
    'username': fields.String(required=True, description='Имя пользователя'),
    'email': fields.String(required=True, description='Email пользователя')
})

login_model = ns.model('Login', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль')
})

register_model = ns.model('Register', {
    'username': fields.String(required=True, description='Имя пользователя'),
    'password': fields.String(required=True, description='Пароль'),
    'email': fields.String(required=True, description='Email пользователя')
})

update_model = ns.model('Update', {
    'email': fields.String(description='Новый email пользователя'),
    'password': fields.String(description='Новый пароль')
})

auth_response = ns.model('AuthResponse', {
    'token': fields.String(description='JWT токен'),
    'user': fields.Nested(user_model),
    'message': fields.String(description='Сообщение об успешной операции')
})

# Функция для загрузки пользователей


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as file:
                return json.load(file)
        else:
            # Если файл не существует, создаем его с тестовыми пользователями
            initial_users = [
                {
                    'id': 1,
                    'username': 'demo',
                    'password': 'demo123',  # В реальном приложении будут хешированные пароли
                    'email': 'demo@example.com'
                },
                {
                    'id': 2,
                    'username': 'test',
                    'password': 'test123',
                    'email': 'test@example.com'
                }
            ]
            save_users(initial_users)
            return initial_users
    except Exception as e:
        logging.error(f"Ошибка при чтении файла пользователей: {e}")
        # Возвращаем тестовых пользователей в случае ошибки
        return [
            {
                'id': 1,
                'username': 'demo',
                'password': 'demo123',
                'email': 'demo@example.com'
            },
            {
                'id': 2,
                'username': 'test',
                'password': 'test123',
                'email': 'test@example.com'
            }
        ]

# Функция для сохранения пользователей


def save_users(users):
    try:
        # Сначала проверяем, существует ли директория
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

        with open(USERS_FILE, 'w') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении файла пользователей: {e}")
        return False


@ns.route('/login')
class Login(Resource):
    """Вход пользователя и получение токена"""
    @ns.expect(login_model)
    @ns.response(200, 'Успешная авторизация', auth_response)
    @ns.response(400, 'Некорректные данные запроса')
    @ns.response(401, 'Неверное имя пользователя или пароль')
    def post(self):
        try:
            data = request.json

            if not data or not data.get('username') or not data.get('password'):
                return {'message': 'Необходимо указать имя пользователя и пароль'}, 400

            # Загружаем пользователей
            users = load_users()

            # Находим пользователя по имени
            user = next(
                (u for u in users if u['username'] == data['username']), None)

            if not user or user['password'] != data['password']:
                return {'message': 'Неверное имя пользователя или пароль'}, 401

            # Создаем JWT-токен
            token = jwt.encode({
                'sub': user['id'],
                'username': user['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, os.environ.get('SECRET_KEY', 'dev-secret-key'))

            response_data = {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                },
                'message': 'Авторизация успешна'
            }

            # Логирование успешной авторизации
            if current_app and current_app.logger:
                current_app.logger.info(
                    f"Успешная авторизация пользователя: {user['username']}")

            return response_data

        except Exception as e:
            logging.error(f"Ошибка при авторизации: {e}")
            return {'message': 'Ошибка авторизации: внутренняя ошибка сервера'}, 500


@ns.route('/register')
class Register(Resource):
    """Регистрация нового пользователя"""
    @ns.expect(register_model)
    @ns.response(201, 'Пользователь успешно зарегистрирован', auth_response)
    @ns.response(400, 'Некорректные данные или пользователь уже существует')
    @ns.response(500, 'Внутренняя ошибка сервера')
    def post(self):
        try:
            data = request.json

            if not data:
                return {'message': 'Отсутствуют данные запроса'}, 400

            if not data.get('username') or not data.get('password') or not data.get('email'):
                return {'message': 'Необходимо указать имя пользователя, пароль и email'}, 400

            # Загружаем существующих пользователей
            users = load_users()

            # Проверяем, существует ли пользователь с таким именем
            if any(u['username'] == data['username'] for u in users):
                return {'message': 'Пользователь с таким именем уже существует'}, 400

            # Создаем нового пользователя
            new_user = {
                'id': len(users) + 1,
                'username': data['username'],
                # В реальном приложении пароль будет хешироваться
                'password': data['password'],
                'email': data['email'],
                'created_at': datetime.datetime.now().isoformat()
            }

            # Добавляем пользователя в список
            users.append(new_user)

            # Сохраняем обновленный список пользователей
            if save_users(users):
                # Генерируем токен для нового пользователя
                token = jwt.encode({
                    'sub': new_user['id'],
                    'username': new_user['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }, os.environ.get('SECRET_KEY', 'dev-secret-key'))

                response_data = {
                    'token': token,
                    'message': 'Пользователь успешно зарегистрирован',
                    'user': {
                        'id': new_user['id'],
                        'username': new_user['username'],
                        'email': new_user['email']
                    }
                }

                # Логирование успешной регистрации
                if current_app and current_app.logger:
                    current_app.logger.info(
                        f"Зарегистрирован новый пользователь: {new_user['username']}")

                return response_data, 201
            else:
                return {'message': 'Ошибка при регистрации пользователя'}, 500

        except Exception as e:
            logging.error(f"Ошибка при регистрации пользователя: {e}")
            return {'message': 'Ошибка регистрации: внутренняя ошибка сервера'}, 500


@ns.route('/me')
class Me(Resource):
    """Получение данных текущего пользователя"""
    @ns.doc('get_current_user', security='Bearer Auth')
    @ns.response(200, 'Данные пользователя получены', user_model)
    @ns.response(401, 'Требуется авторизация')
    @ns.response(404, 'Пользователь не найден')
    def get(self):
        try:
            # Получаем токен из заголовка Authorization
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return {'message': 'Отсутствует или неверный токен авторизации'}, 401

            token = auth_header.split(' ')[1]

            try:
                # Декодируем токен
                payload = jwt.decode(token, os.environ.get(
                    'SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
                user_id = payload['sub']

                # Загружаем пользователей и находим пользователя по ID
                users = load_users()
                user = next((u for u in users if u['id'] == user_id), None)

                if not user:
                    return {'message': 'Пользователь не найден'}, 404

                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }

            except jwt.ExpiredSignatureError:
                return {'message': 'Срок действия токена истек'}, 401
            except jwt.InvalidTokenError:
                return {'message': 'Неверный токен'}, 401

        except Exception as e:
            logging.error(f"Ошибка при получении данных пользователя: {e}")
            return {'message': 'Внутренняя ошибка сервера'}, 500


@ns.route('/update')
class UpdateUser(Resource):
    """Обновление данных пользователя"""
    @ns.doc('update_user', security='Bearer Auth')
    @ns.expect(update_model)
    @ns.response(200, 'Данные пользователя обновлены', user_model)
    @ns.response(400, 'Некорректные данные запроса')
    @ns.response(401, 'Требуется авторизация')
    @ns.response(404, 'Пользователь не найден')
    @ns.response(500, 'Внутренняя ошибка сервера')
    def put(self):
        try:
            # Получаем токен из заголовка Authorization
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return {'message': 'Отсутствует или неверный токен авторизации'}, 401

            token = auth_header.split(' ')[1]

            try:
                # Декодируем токен
                payload = jwt.decode(token, os.environ.get(
                    'SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
                user_id = payload['sub']

                # Получаем данные для обновления
                data = request.json
                if not data:
                    return {'message': 'Нет данных для обновления'}, 400

                # Загружаем пользователей
                users = load_users()

                # Находим индекс пользователя для обновления
                user_index = next((i for i, u in enumerate(users)
                                   if u['id'] == user_id), None)

                if user_index is None:
                    return {'message': 'Пользователь не найден'}, 404

                # Обновляем данные пользователя
                if 'email' in data:
                    users[user_index]['email'] = data['email']

                if 'password' in data:
                    # В реальном приложении пароль будет хешироваться
                    users[user_index]['password'] = data['password']

                # Сохраняем обновленный список пользователей
                if save_users(users):
                    return {
                        'id': users[user_index]['id'],
                        'username': users[user_index]['username'],
                        'email': users[user_index]['email']
                    }
                else:
                    return {'message': 'Ошибка при обновлении данных пользователя'}, 500

            except jwt.ExpiredSignatureError:
                return {'message': 'Срок действия токена истек'}, 401
            except jwt.InvalidTokenError:
                return {'message': 'Неверный токен'}, 401

        except Exception as e:
            logging.error(f"Ошибка при обновлении данных пользователя: {e}")
            return {'message': 'Внутренняя ошибка сервера'}, 500

from flask import Blueprint, request, jsonify
import jwt
import datetime
import os
import json
import logging

# Создаем Blueprint для авторизации
auth_bp = Blueprint('auth', __name__)

# Путь к файлу хранения пользователей
USERS_FILE = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'users.json')

# Проверяем наличие директории для данных
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

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


@auth_bp.route('/login', methods=['POST'])
def login():
    """Вход пользователя и получение токена"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Необходимо указать имя пользователя и пароль'}), 400

        # Загружаем пользователей
        users = load_users()

        # Находим пользователя по имени
        user = next(
            (u for u in users if u['username'] == data['username']), None)

        if not user or user['password'] != data['password']:
            return jsonify({'message': 'Неверное имя пользователя или пароль'}), 401

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
        logging.info(f"Успешная авторизация пользователя: {user['username']}")

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Ошибка при авторизации: {e}")
        return jsonify({'message': 'Ошибка авторизации: внутренняя ошибка сервера'}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'Отсутствуют данные запроса'}), 400

        if not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'message': 'Необходимо указать имя пользователя, пароль и email'}), 400

        # Загружаем существующих пользователей
        users = load_users()

        # Проверяем, существует ли пользователь с таким именем
        if any(u['username'] == data['username'] for u in users):
            return jsonify({'message': 'Пользователь с таким именем уже существует'}), 400

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
            logging.info(
                f"Зарегистрирован новый пользователь: {new_user['username']}")

            return jsonify(response_data), 201
        else:
            return jsonify({'message': 'Ошибка при регистрации пользователя'}), 500

    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        return jsonify({'message': 'Ошибка регистрации: внутренняя ошибка сервера'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Получение данных текущего пользователя"""
    try:
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Отсутствует или неверный токен авторизации'}), 401

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
                return jsonify({'message': 'Пользователь не найден'}), 404

            return jsonify({
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            })

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Срок действия токена истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Неверный токен'}), 401

    except Exception as e:
        logging.error(f"Ошибка при получении данных пользователя: {e}")
        return jsonify({'message': 'Внутренняя ошибка сервера'}), 500


@auth_bp.route('/update', methods=['PUT'])
def update_user():
    """Обновление данных пользователя"""
    try:
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Отсутствует или неверный токен авторизации'}), 401

        token = auth_header.split(' ')[1]

        try:
            # Декодируем токен
            payload = jwt.decode(token, os.environ.get(
                'SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
            user_id = payload['sub']

            # Получаем данные для обновления
            data = request.get_json()
            if not data:
                return jsonify({'message': 'Нет данных для обновления'}), 400

            # Загружаем пользователей
            users = load_users()

            # Находим индекс пользователя для обновления
            user_index = next((i for i, u in enumerate(users)
                               if u['id'] == user_id), None)

            if user_index is None:
                return jsonify({'message': 'Пользователь не найден'}), 404

            # Обновляем данные пользователя
            if 'email' in data:
                users[user_index]['email'] = data['email']

            if 'password' in data:
                # В реальном приложении пароль будет хешироваться
                users[user_index]['password'] = data['password']

            # Сохраняем обновленный список пользователей
            if save_users(users):
                return jsonify({
                    'id': users[user_index]['id'],
                    'username': users[user_index]['username'],
                    'email': users[user_index]['email']
                })
            else:
                return jsonify({'message': 'Ошибка при обновлении данных пользователя'}), 500

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Срок действия токена истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Неверный токен'}), 401

    except Exception as e:
        logging.error(f"Ошибка при обновлении данных пользователя: {e}")
        return jsonify({'message': 'Внутренняя ошибка сервера'}), 500

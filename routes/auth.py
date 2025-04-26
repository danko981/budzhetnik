from flask import Blueprint, request, jsonify
import jwt
import datetime
import os

# Создаем Blueprint
auth_routes = Blueprint('auth', __name__)

# Заглушка для пользователей (в реальном приложении будет база данных)
users = [
    {
        'id': 1,
        'username': 'demo',
        'password': 'demo123',  # В реальном приложении будут хешированные пароли
        'email': 'demo@example.com'
    }
]

# Маршрут для входа


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Необходимо указать имя пользователя и пароль'}), 400

    # Находим пользователя по имени
    user = next((u for u in users if u['username'] == data['username']), None)

    if not user or user['password'] != data['password']:
        return jsonify({'message': 'Неверные учетные данные'}), 401

    # Создаем JWT-токен
    token = jwt.encode({
        'sub': user['id'],
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, os.environ.get('SECRET_KEY', 'dev-secret-key'))

    return jsonify({
        'access_token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
    })

# Маршрут для регистрации


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Необходимо указать имя пользователя, пароль и email'}), 400

    # Проверяем, существует ли пользователь с таким именем
    if any(u['username'] == data['username'] for u in users):
        return jsonify({'message': 'Пользователь с таким именем уже существует'}), 400

    # Создаем нового пользователя
    new_user = {
        'id': len(users) + 1,
        'username': data['username'],
        # В реальном приложении пароль будет хешироваться
        'password': data['password'],
        'email': data['email']
    }

    users.append(new_user)

    return jsonify({
        'message': 'Пользователь успешно зарегистрирован',
        'user': {
            'id': new_user['id'],
            'username': new_user['username'],
            'email': new_user['email']
        }
    }), 201

# Маршрут для получения данных текущего пользователя


@auth_routes.route('/me', methods=['GET'])
def get_current_user():
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

        # Находим пользователя по ID
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

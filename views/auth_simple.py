from flask import Blueprint, request, jsonify, current_app, make_response
import jwt
import datetime
import os
import json
import logging
from functools import wraps

# Создаем Blueprint для авторизации
auth_bp = Blueprint('auth', __name__)

# Путь к файлу хранения пользователей
USERS_FILE = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'users.json')

# Проверяем наличие директории для данных
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('auth_simple')

# Декоратор для добавления CORS-заголовков


def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Предварительная обработка OPTIONS запросов
        if request.method == 'OPTIONS':
            resp = make_response()
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
            resp.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
            resp.headers.add('Access-Control-Max-Age', '3600')
            resp.status_code = 200
            return resp

        try:
            response = f(*args, **kwargs)

            # Обработка случая, когда response - это кортеж (данные, код состояния)
            if isinstance(response, tuple):
                if len(response) == 2:
                    data, status_code = response
                    # Проверяем, что data не является объектом Response
                    if hasattr(data, 'headers'):
                        # Если это уже объект Response, просто добавляем заголовки
                        resp = data
                    else:
                        # Создаем объект Response из данных
                        resp = make_response(jsonify(data), status_code)
                else:
                    resp = make_response(response)
            else:
                # Если это уже объект Response
                if hasattr(response, 'headers'):
                    resp = response
                else:
                    # Создаем объект Response из данных
                    resp = make_response(jsonify(response))

            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
            resp.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
            resp.headers.add('Access-Control-Max-Age', '3600')
            return resp
        except Exception as e:
            logger.error(f"Ошибка в CORS-декораторе: {e}", exc_info=True)
            error_response = make_response(
                jsonify({"message": f"Внутренняя ошибка сервера: {str(e)}"}), 500)
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            error_response.headers.add(
                'Access-Control-Allow-Headers', 'Content-Type,Authorization')
            error_response.headers.add(
                'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return error_response
    return decorated_function


# Загрузка пользователей с кэшированием
_users_cache = None
_last_load_time = None


def load_users():
    global _users_cache, _last_load_time
    current_time = datetime.datetime.now()

    # Если кэш пуст или прошло более 5 минут с последней загрузки
    if _users_cache is None or _last_load_time is None or (current_time - _last_load_time).seconds > 300:
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as file:
                    _users_cache = json.load(file)
                    _last_load_time = current_time
                    logger.info(
                        f"Пользователи загружены из файла: {USERS_FILE}")
                    return _users_cache
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
                _users_cache = initial_users
                _last_load_time = current_time
                logger.info("Создан файл с тестовыми пользователями")
                return _users_cache
        except Exception as e:
            logger.error(f"Ошибка при чтении файла пользователей: {e}")
            # Возвращаем тестовых пользователей в случае ошибки
            fallback_users = [
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
            _users_cache = fallback_users
            _last_load_time = current_time
            return fallback_users
    else:
        # Возвращаем кэшированные данные
        return _users_cache


def save_users(users):
    global _users_cache, _last_load_time
    try:
        # Сначала проверяем, существует ли директория
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

        with open(USERS_FILE, 'w') as file:
            json.dump(users, file, ensure_ascii=False, indent=4)

        # Обновляем кэш
        _users_cache = users
        _last_load_time = datetime.datetime.now()
        logger.info(f"Пользователи сохранены в файл: {USERS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла пользователей: {e}")
        return False


@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@add_cors_headers
def login():
    """Вход пользователя и получение токена"""
    try:
        # Проверяем, что данные пришли в правильном формате
        if not request.is_json:
            logger.warning("Получены неверные данные, не JSON формат")
            return {"message": "Ожидается JSON-формат"}, 400

        data = request.get_json()

        if data is None:
            logger.warning("Получен пустой JSON или неверный формат")
            return {"message": "Неверный формат данных"}, 400

        logger.info(
            f"Получен запрос на авторизацию пользователя: {data.get('username', 'unknown')}")

        if not data or not data.get('username') or not data.get('password'):
            logger.warning("Неполные данные для авторизации")
            return {"message": 'Необходимо указать имя пользователя и пароль'}, 400

        # Загружаем пользователей
        users = load_users()

        # Находим пользователя по имени
        user = next(
            (u for u in users if u['username'] == data['username']), None)

        if not user or user['password'] != data['password']:
            logger.warning(
                f"Неудачная попытка авторизации для пользователя: {data['username']}")
            return {"message": 'Неверное имя пользователя или пароль'}, 401

        # Создаем JWT-токен
        token = jwt.encode({
            'sub': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, current_app.config.get('SECRET_KEY', 'dev-secret-key'))

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
        logger.info(f"Успешная авторизация пользователя: {user['username']}")

        return response_data

    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}", exc_info=True)
        return {"message": f'Ошибка авторизации: внутренняя ошибка сервера', "error": str(e)}, 500


@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@add_cors_headers
def register():
    """Регистрация нового пользователя"""
    try:
        # Проверяем, что данные пришли в правильном формате
        if not request.is_json:
            logger.warning(
                "Получены неверные данные для регистрации, не JSON формат")
            return {"message": "Ожидается JSON-формат"}, 400

        data = request.get_json()

        if data is None:
            logger.warning(
                "Получен пустой JSON или неверный формат при регистрации")
            return {"message": "Неверный формат данных"}, 400

        logger.info(
            f"Получен запрос на регистрацию пользователя: {data.get('username', 'unknown')}")

        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            logger.warning("Неполные данные для регистрации")
            return {"message": 'Необходимо указать имя пользователя, пароль и email'}, 400

        # Загружаем существующих пользователей
        users = load_users()

        # Проверяем, существует ли пользователь с таким именем
        if any(u['username'] == data['username'] for u in users):
            logger.warning(
                f"Попытка регистрации существующего пользователя: {data['username']}")
            return {"message": 'Пользователь с таким именем уже существует'}, 400

        # Определяем следующий ID
        next_id = max([u['id'] for u in users], default=0) + 1

        # Создаем нового пользователя
        new_user = {
            'id': next_id,
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
            }, current_app.config.get('SECRET_KEY', 'dev-secret-key'))

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
            logger.info(
                f"Зарегистрирован новый пользователь: {new_user['username']}")

            return response_data, 201
        else:
            logger.error(
                f"Ошибка при сохранении данных нового пользователя: {data['username']}")
            return {"message": 'Ошибка при регистрации пользователя'}, 500

    except Exception as e:
        logger.error(
            f"Ошибка при регистрации пользователя: {e}", exc_info=True)
        return {"message": f'Ошибка регистрации: внутренняя ошибка сервера', "error": str(e)}, 500


@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
@add_cors_headers
def get_current_user():
    """Получение данных текущего пользователя"""
    try:
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(
                "Попытка доступа к данным пользователя без токена авторизации")
            return {"message": 'Отсутствует или неверный токен авторизации'}, 401

        token = auth_header.split(' ')[1]

        try:
            # Декодируем токен
            payload = jwt.decode(token, current_app.config.get(
                'SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
            user_id = payload['sub']

            # Загружаем пользователей и находим пользователя по ID
            users = load_users()
            user = next((u for u in users if u['id'] == user_id), None)

            if not user:
                logger.warning(f"Пользователь с ID {user_id} не найден")
                return {"message": 'Пользователь не найден'}, 404

            logger.info(f"Запрошены данные пользователя: {user['username']}")
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }

        except jwt.ExpiredSignatureError:
            logger.warning("Истекший токен авторизации")
            return {"message": 'Срок действия токена истек'}, 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Недействительный токен: {e}")
            return {"message": 'Неверный токен'}, 401

    except Exception as e:
        logger.error(
            f"Ошибка при получении данных пользователя: {e}", exc_info=True)
        return {"message": 'Внутренняя ошибка сервера', "error": str(e)}, 500


@auth_bp.route('/update', methods=['PUT', 'OPTIONS'])
@add_cors_headers
def update_user():
    """Обновление данных пользователя"""
    try:
        # Проверяем, что данные пришли в правильном формате
        if not request.is_json:
            logger.warning(
                "Получены неверные данные для обновления, не JSON формат")
            return {"message": "Ожидается JSON-формат"}, 400

        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(
                "Попытка обновления данных пользователя без токена авторизации")
            return {"message": 'Отсутствует или неверный токен авторизации'}, 401

        token = auth_header.split(' ')[1]

        try:
            # Декодируем токен
            payload = jwt.decode(token, current_app.config.get(
                'SECRET_KEY', 'dev-secret-key'), algorithms=['HS256'])
            user_id = payload['sub']

            # Получаем данные для обновления
            data = request.get_json()
            if not data:
                logger.warning(
                    "Попытка обновления данных пользователя без данных")
                return {"message": 'Нет данных для обновления'}, 400

            # Загружаем пользователей
            users = load_users()

            # Находим индекс пользователя для обновления
            user_index = next((i for i, u in enumerate(users)
                               if u['id'] == user_id), None)

            if user_index is None:
                logger.warning(
                    f"Пользователь с ID {user_id} не найден для обновления")
                return {"message": 'Пользователь не найден'}, 404

            logger.info(
                f"Обновление данных пользователя: {users[user_index]['username']}")

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
                logger.error(
                    f"Ошибка при сохранении обновленных данных пользователя: {users[user_index]['username']}")
                return {"message": 'Ошибка при обновлении данных пользователя'}, 500

        except jwt.ExpiredSignatureError:
            logger.warning("Истекший токен авторизации при обновлении данных")
            return {"message": 'Срок действия токена истек'}, 401
        except jwt.InvalidTokenError as e:
            logger.warning(
                f"Недействительный токен при обновлении данных: {e}")
            return {"message": 'Неверный токен'}, 401

    except Exception as e:
        logger.error(
            f"Ошибка при обновлении данных пользователя: {e}", exc_info=True)
        return {"message": 'Внутренняя ошибка сервера', "error": str(e)}, 500

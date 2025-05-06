from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from services.auth_service import AuthService
import logging

# Создаем Namespace для авторизации
ns = Namespace('auth', description='Операции с аутентификацией и авторизацией')

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

token_model = ns.model('Token', {
    'access_token': fields.String(description='JWT токен доступа'),
    'refresh_token': fields.String(description='JWT токен обновления')
})

auth_response = ns.model('AuthResponse', {
    'access_token': fields.String(description='JWT токен доступа'),
    'refresh_token': fields.String(description='JWT токен обновления'),
    'user': fields.Nested(user_model),
    'message': fields.String(description='Сообщение об успешной операции')
})

refresh_response = ns.model('RefreshResponse', {
    'access_token': fields.String(description='Новый JWT токен доступа')
})


@ns.route('/login')
class Login(Resource):
    """Вход пользователя и получение токена"""
    @ns.expect(login_model)
    @ns.response(200, 'Успешная авторизация', auth_response)
    @ns.response(400, 'Некорректные данные запроса')
    @ns.response(401, 'Неверное имя пользователя или пароль')
    @ns.response(500, 'Внутренняя ошибка сервера')
    def post(self):
        try:
            data = request.json

            if not data or not data.get('username') or not data.get('password'):
                return {'error': 'Необходимо указать имя пользователя и пароль'}, 400

            result, status_code = AuthService.login_user(
                username=data['username'],
                password=data['password']
            )

            return result, status_code

        except Exception as e:
            current_app.logger.error(f"Ошибка при авторизации: {str(e)}")
            return {'error': 'Внутренняя ошибка сервера'}, 500


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

            if not data or not data.get('username') or not data.get('password') or not data.get('email'):
                return {'error': 'Необходимо указать имя пользователя, пароль и email'}, 400

            result, status_code = AuthService.register_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            return result, status_code

        except Exception as e:
            current_app.logger.error(f"Ошибка при регистрации: {str(e)}")
            return {'error': 'Внутренняя ошибка сервера'}, 500


@ns.route('/me')
class Me(Resource):
    """Получение данных текущего пользователя"""
    @jwt_required()
    @ns.doc(security='Bearer Auth')
    @ns.response(200, 'Данные пользователя получены', user_model)
    @ns.response(401, 'Требуется авторизация')
    def get(self):
        try:
            return {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        except Exception as e:
            current_app.logger.error(
                f"Ошибка при получении данных пользователя: {str(e)}")
            return {'error': 'Внутренняя ошибка сервера'}, 500


@ns.route('/update')
class UpdateUser(Resource):
    """Обновление данных пользователя"""
    @jwt_required()
    @ns.doc(security='Bearer Auth')
    @ns.expect(update_model)
    @ns.response(200, 'Данные пользователя обновлены', user_model)
    @ns.response(400, 'Некорректные данные запроса')
    @ns.response(401, 'Требуется авторизация')
    @ns.response(404, 'Пользователь не найден')
    @ns.response(500, 'Внутренняя ошибка сервера')
    def put(self):
        try:
            data = request.json

            if not data:
                return {'error': 'Нет данных для обновления'}, 400

            user_id = get_jwt_identity()
            result, status_code = AuthService.update_user(user_id, data)

            return result, status_code

        except Exception as e:
            current_app.logger.error(
                f"Ошибка при обновлении пользователя: {str(e)}")
            return {'error': 'Внутренняя ошибка сервера'}, 500


@ns.route('/refresh')
class RefreshToken(Resource):
    """Обновление токена доступа"""
    @jwt_required(refresh=True)
    @ns.doc(security='Bearer Auth')
    @ns.response(200, 'Токен обновлен', refresh_response)
    @ns.response(401, 'Требуется авторизация')
    @ns.response(500, 'Внутренняя ошибка сервера')
    def post(self):
        try:
            result, status_code = AuthService.refresh_token(current_user)
            return result, status_code
        except Exception as e:
            current_app.logger.error(f"Ошибка при обновлении токена: {str(e)}")
            return {'error': 'Внутренняя ошибка сервера'}, 500

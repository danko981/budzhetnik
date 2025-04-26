import logging  # Для логирования
from logging.handlers import RotatingFileHandler  # Для ротации лог-файлов
import os
from flask import Flask, jsonify
from flask_restx import Api  # Импорт Api из flask_restx
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException  # Для стандартных HTTP ошибок
from marshmallow import ValidationError  # Для ошибок валидации Marshmallow
from config import config
from .models import User  # Импортируем User для колбэков JWT
from flask_cors import CORS  # Импортируем CORS

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()

# Создаем объект Api вместо прямого app
# Добавим информацию для Swagger UI
authorizations = {  # Настройка для кнопки Authorize в Swagger UI
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in 'Bearer <your_token>' to authorize."
    }
}
api = Api(
    version='1.0',
    title='Budgetnik API',
    description='API для управления личным бюджетом',
    authorizations=authorizations,
    security='Bearer Auth'  # Требовать авторизацию по умолчанию для всех эндпоинтов Api
)

# --- JWT Callbacks ---


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify(message="Token has expired"), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify(message="Signature verification failed"), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    # Этот колбэк может перекрываться стандартной обработкой 401 от Flask-RESTx/JWT
    # Проверим, как он будет работать вместе с security='Bearer Auth'
    return jsonify(message="Missing Authorization Header"), 401
# --- End JWT Callbacks ---

# --- Глобальные обработчики ошибок ---


@api.errorhandler(HTTPException)
def handle_http_exception(error):
    """Стандартный обработчик HTTP ошибок для API."""
    # logging.getLogger(__name__).error(f"HTTPException: {error.code} - {error.description}")
    return {'message': error.description or error.name}, error.code


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    """Обработчик ошибок валидации Marshmallow."""
    return error.messages, 400


@api.errorhandler(Exception)
def handle_generic_exception(error):
    """Обработчик непредвиденных ошибок."""
    # logging.getLogger(__name__).exception("Unhandled Exception")
    # В реальном приложении здесь будет детальное логирование ошибки
    return {'message': 'An internal server error occurred.'}, 500
# --- Конец обработчиков ошибок ---


def create_app(config_name='default'):
    app = Flask(__name__)
    app_config = config[config_name]
    app.config.from_object(app_config)

    # --- Инициализация CORS ---
    # Разрешаем запросы с определенных доменов (или со всех для разработки)
    # Укажите реальный URL вашего фронтенда для production
    # Добавьте URL вашего фронтенда
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Если вы не знаете порт заранее или для простой разработки:
    # origins = "*"
    CORS(app, resources={r"/api/*": {"origins": origins}},
         supports_credentials=True)
    # resources={r"/api/*"} - применяем CORS только к путям API
    # supports_credentials=True - важно для отправки куки или заголовка Authorization

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    # Инициализируем Api с app
    api.init_app(app, doc='/api/docs')  # Указываем путь для Swagger UI

    # --- Настройка логирования ---
    if not app.debug and not app.testing:  # Не настраиваем в debug или testing режимах
        # Устанавливаем уровень лога
        log_level = getattr(
            logging, app_config.LOG_LEVEL.upper(), logging.INFO)
        app.logger.setLevel(log_level)

        # Создаем папку для логов, если ее нет
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Файловый обработчик с ротацией
        file_handler = RotatingFileHandler(
            'logs/budgetnik.log', maxBytes=10240, backupCount=10)
        # Форматтер логов
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        # Добавляем обработчик к логгеру приложения
        app.logger.addHandler(file_handler)

        # Добавляем информацию о запуске в лог
        app.logger.info('Budgetnik App Startup')
    # -----------------------------

    # --- Регистрация Namespaces ---
    from .views.auth_restx import ns as auth_ns
    api.add_namespace(auth_ns, path='/api/v1/auth')

    from .views.categories_restx import ns as categories_ns
    api.add_namespace(categories_ns, path='/api/v1/categories')

    from .views.transactions_restx import ns as transactions_ns
    api.add_namespace(transactions_ns, path='/api/v1/transactions')

    from .views.budgets_restx import ns as budgets_ns
    api.add_namespace(budgets_ns, path='/api/v1/budgets')

    from .views.reports_restx import ns as reports_ns
    api.add_namespace(reports_ns, path='/api/v1/reports')

    from .views.calculator_restx import ns as calculator_ns
    api.add_namespace(calculator_ns, path='/api/v1/calculator')

    from .views.support_restx import ns as support_ns
    api.add_namespace(support_ns, path='/api/v1/support')
    # -----------------------------

    # --- Эндпоинты вне API ---
    @app.route('/health')
    def health_check():
        return {"status": "ok"}

    return app

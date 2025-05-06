from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_restx import Api
import os
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Определение глобальных компонентов
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()

# Настройка API с документацией Swagger
authorizations = {
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
    security='Bearer Auth'
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger('budgetnik')

# Настройка JWT колбэков


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    from models import User
    identity = jwt_data["sub"]
    return User.query.get(identity)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Срок действия токена истек"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Неверный токен"}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"error": "Отсутствует токен авторизации"}), 401


def create_app(config_name='default'):
    # Создание экземпляра приложения
    app = Flask(__name__,
                static_folder='static',
                static_url_path='')  # Важное изменение: пустой путь для статики

    # Конфигурация из объекта config
    from config import config as app_config
    app.config.from_object(app_config[config_name])

    # Улучшенная настройка CORS
    CORS(app,
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization",
                        "X-Requested-With", "Cache-Control", "Pragma", "Expires"],
         expose_headers=['Content-Type', 'Authorization'])

    # Дополнительная конфигурация
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
    # Для корректного отображения кириллицы
    app.config['JSON_AS_ASCII'] = False

    # Инициализация компонентов с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    api.init_app(app, doc='/api/docs')

    # Регистрация всех пространств имен API
    from views.auth_restx import ns as auth_ns
    from views.categories_restx import ns as categories_ns
    from views.transactions_restx import ns as transactions_ns
    from views.budgets_restx import ns as budgets_ns
    from views.reports_restx import ns as reports_ns
    from views.calculator_restx import ns as calculator_ns
    from views.support_restx import ns as support_ns

    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(categories_ns, path='/api/v1/categories')
    api.add_namespace(transactions_ns, path='/api/v1/transactions')
    api.add_namespace(budgets_ns, path='/api/v1/budgets')
    api.add_namespace(reports_ns, path='/api/v1/reports')
    api.add_namespace(calculator_ns, path='/api/v1/calculator')
    api.add_namespace(support_ns, path='/api/v1/support')

    # API статус
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'online',
            'message': 'API сервер Budgetnik работает',
            'version': '1.1.0'
        })

    # Маршрут для проверки здоровья системы
    @app.route('/health')
    def health_check():
        return {"status": "ok"}

    # Специальный маршрут для assets
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

    # Маршрут для favicon
    @app.route('/favicon.svg')
    def serve_favicon():
        return send_from_directory(app.static_folder, 'favicon.svg')

    # Маршрут для отдачи статических файлов фронтенда
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        # Проверяем, если запрос начинается с /api
        if path.startswith('api/'):
            # 404 для API, которые не найдены
            return jsonify({"error": "Маршрут API не найден"}), 404

        # Если это реальный файл, возвращаем его
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)

        # Для всех остальных путей возвращаем index.html (для React Router)
        return send_from_directory(app.static_folder, 'index.html')

    # Обработчик ошибки 404
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Ресурс не найден"}), 404
        return send_from_directory(app.static_folder, 'index.html')

    # Обработчик ошибки 500
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Внутренняя ошибка сервера: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера", "message": str(e)}), 500

    logger.info("Приложение Budgetnik успешно создано")
    return app


# Запуск приложения
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Запуск приложения на порту {port}")
    app.run(host='0.0.0.0', port=port,
            debug=app.config['DEBUG'], threaded=True)

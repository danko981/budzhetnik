from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_restx import Api
import os
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


def create_app():
    # Создание экземпляра приложения
    app = Flask(__name__, static_folder='static')
    CORS(app)

    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///budgetnik.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get(
        'JWT_SECRET_KEY', app.config['SECRET_KEY'])

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
            'version': '1.0.0'
        })

    # Маршрут для отдачи статических файлов фронтенда
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    # Обработчик ошибки 404
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Resource not found"}), 404
        return send_from_directory(app.static_folder, 'index.html')

    return app


# Запуск приложения
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

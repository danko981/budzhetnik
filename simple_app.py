from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from views.auth_simple import auth_bp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Загрузка переменных окружения
load_dotenv()


def create_app():
    # Создание экземпляра приложения
    app = Flask(__name__, static_folder='static')

    # Расширенная настройка CORS
    CORS(app,
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

    # Регистрация Blueprint для авторизации
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

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

    # Предварительная обработка запросов (для CORS)
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app


# Запуск приложения
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

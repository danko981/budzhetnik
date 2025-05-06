from flask import Flask, send_from_directory, jsonify, request, make_response
from flask_cors import CORS
import os
import logging
import traceback
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
logger = logging.getLogger('simple_app')

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
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

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

    # Обработчик CORS preflight запросов для всех маршрутов
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        response.status_code = 200
        return response

    # Обработчик ошибки 404
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Resource not found"}), 404
        return send_from_directory(app.static_folder, 'index.html')

    # Обработчик ошибки 500
    @app.errorhandler(500)
    def server_error(e):
        logger.error(
            f"Внутренняя ошибка сервера: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

    # Обработчик ошибки таймаута
    @app.errorhandler(408)
    def timeout_error(e):
        logger.error(f"Ошибка таймаута: {str(e)}")
        return jsonify({"error": "Request timeout", "message": "Запрос занял слишком много времени"}), 408

    # Предварительная обработка запросов (для CORS)
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        # Кеширование preflight запросов на 1 час
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    logger.info("Приложение Budgetnik (упрощенная версия) успешно создано")
    return app


# Запуск приложения
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Запуск приложения на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

from routes.calculator import calculator_routes
from routes.auth import auth_routes
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Создание экземпляра приложения
app = Flask(__name__, static_folder='static')
CORS(app)

# Конфигурация
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'

# Импорт API-маршрутов
# from routes.transactions import transactions_routes
# from routes.categories import categories_routes
# from routes.budgets import budgets_routes
# from routes.reports import reports_routes

# Регистрация маршрутов
app.register_blueprint(auth_routes, url_prefix='/api/v1/auth')
app.register_blueprint(calculator_routes, url_prefix='/api/v1/calculator')
# app.register_blueprint(transactions_routes, url_prefix='/api/v1/transactions')
# app.register_blueprint(categories_routes, url_prefix='/api/v1/categories')
# app.register_blueprint(budgets_routes, url_prefix='/api/v1/budgets')
# app.register_blueprint(reports_routes, url_prefix='/api/v1/reports')

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


# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

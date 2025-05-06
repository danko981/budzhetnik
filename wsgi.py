import os
from app import create_app

# Определяем конфигурацию из переменной окружения или используем development по умолчанию
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

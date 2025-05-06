import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    """Базовый класс конфигурации."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'INFO'

    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///budgetnik.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT настройки
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24 часа в секундах

    # CORS настройки
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]


class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = "*"  # Разрешаем все источники в режиме разработки


class TestingConfig(Config):
    """Конфигурация для тестирования."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Используем in-memory БД
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 минут для тестов


class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    # В продакшене все настройки берутся из переменных окружения
    # Проверим наличие обязательных параметров
    @classmethod
    def init_app(cls, app):
        # Проверка наличия и валидности ключевых переменных
        assert os.environ.get('SECRET_KEY'), "SECRET_KEY must be set"
        assert os.environ.get('DATABASE_URL'), "DATABASE_URL must be set"


# Словарь доступных конфигураций
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

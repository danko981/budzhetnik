#!/bin/bash

# Настройка переменных окружения
export FLASK_APP=simple_app.py
export FLASK_DEBUG=1
export PYTHONPATH=.
export DEBUG=True
export SECRET_KEY=dev-secret-key
export PORT=8000

# Активация виртуального окружения, если оно существует
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
fi

# Проверка и установка зависимостей
echo "Проверка и установка зависимостей..."
pip install -r requirements.txt

# Создание директории для данных, если она не существует
mkdir -p data

# Запуск приложения
echo "Запуск упрощенного API Budgetnik..."
python simple_app.py 
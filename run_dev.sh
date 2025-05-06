#!/bin/bash

# Запуск приложения Budgetnik в режиме разработки

# Переменные
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Проверяем, существует ли виртуальное окружение
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения Python..."
    python3 -m venv venv || { echo "Не удалось создать виртуальное окружение"; exit 1; }
fi

# Активация виртуального окружения
echo "Активация виртуального окружения..."
source venv/bin/activate || { echo "Не удалось активировать виртуальное окружение"; exit 1; }

# Установка зависимостей Python
if [ -f "requirements.txt" ]; then
    echo "Установка Python зависимостей..."
    pip install -r requirements.txt || { echo "Ошибка при установке Python зависимостей"; exit 1; }
fi

# Создание файла .env с настройками для разработки
if [ ! -f ".env" ]; then
    echo "Создание файла .env с настройками для разработки..."
    cat > .env << EOF
DEBUG=True
FLASK_CONFIG=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///budgetnik.db
PORT=$BACKEND_PORT
EOF
fi

# Запускаем бэкенд
echo "Запуск бэкенда на порту $BACKEND_PORT..."
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export FLASK_CONFIG=development
export DEBUG=True
export PORT=$BACKEND_PORT
python3 wsgi.py &
BACKEND_PID=$!

# Переходим в директорию фронтенда и запускаем его
if [ -d "frontend" ]; then
    echo "Запуск фронтенда на порту $FRONTEND_PORT..."
    cd frontend
    
    # Проверяем наличие пакетов node_modules
    if [ ! -d "node_modules" ]; then
        echo "Установка зависимостей для фронтенда..."
        npm install || { echo "Ошибка при установке зависимостей для фронтенда"; exit 1; }
    fi
    
    # Запускаем dev сервер (предполагаем использование Vite)
    npm run dev &
    FRONTEND_PID=$!
    cd ..
else
    echo "Директория фронтенда не найдена"
    FRONTEND_PID=""
fi

# Функция для корректного завершения всех процессов при выходе
cleanup() {
    echo "Завершение работы процессов..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Устанавливаем обработчик сигналов для корректного завершения
trap cleanup INT TERM

echo "Приложение запущено в режиме разработки"
echo "Бэкенд: http://localhost:$BACKEND_PORT"
echo "API Документация: http://localhost:$BACKEND_PORT/api/docs"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "Фронтенд: http://localhost:$FRONTEND_PORT"
fi
echo "Нажмите Ctrl+C для завершения работы"

# Ожидаем завершения
wait 
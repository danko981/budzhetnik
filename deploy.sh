#!/bin/bash

# Скрипт для сборки и деплоя приложения Budgetnik

echo "🚀 Начинаем процесс сборки и деплоя приложения Budgetnik..."

# Переменные
FRONTEND_DIR="frontend"

# Проверка наличия необходимых программ
command -v npm >/dev/null 2>&1 || { echo "❌ Требуется npm, но он не установлен. Установите Node.js и npm."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Требуется python3, но он не установлен."; exit 1; }

# Сборка фронтенда
echo "📦 Сборка фронтенда..."
cd "$FRONTEND_DIR" || { echo "❌ Директория $FRONTEND_DIR не найдена"; exit 1; }

# Установка зависимостей
echo "📥 Установка зависимостей npm..."
npm install || { echo "❌ Ошибка при установке зависимостей"; exit 1; }

# Сборка проекта
echo "🛠️ Сборка проекта..."
npm run build || { echo "❌ Ошибка при сборке проекта"; exit 1; }

echo "✅ Фронтенд успешно собран!"
cd ..

# Проверка и создание виртуального окружения Python
echo "🐍 Настройка окружения Python..."
if [ ! -d "venv" ]; then
    echo "🔨 Создание виртуального окружения Python..."
    python3 -m venv venv || { echo "❌ Не удалось создать виртуальное окружение"; exit 1; }
fi

# Активация виртуального окружения
echo "🔌 Активация виртуального окружения..."
source venv/bin/activate || { echo "❌ Не удалось активировать виртуальное окружение"; exit 1; }

# Установка зависимостей Python
if [ -f "requirements.txt" ]; then
    echo "📥 Установка Python зависимостей..."
    pip install -r requirements.txt || { echo "❌ Ошибка при установке Python зависимостей"; exit 1; }
else
    echo "⚠️ Файл requirements.txt не найден. Устанавливаем базовые зависимости..."
    pip install flask flask-cors gunicorn || { echo "❌ Ошибка при установке базовых Python зависимостей"; exit 1; }
fi

# Создание директории для статических файлов
echo "📁 Настройка директории для статических файлов..."
mkdir -p static

# Копирование собранных файлов фронтенда в директорию статических файлов
echo "📋 Копирование файлов фронтенда в директорию статических файлов..."
cp -r frontend/dist/* static/ || { echo "❌ Ошибка при копировании файлов"; exit 1; }

# Создаем файл .env если его нет
if [ ! -f ".env" ]; then
    echo "📝 Создание файла .env с настройками по умолчанию..."
    cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
DATABASE_URL=sqlite:///app.db
EOF
fi

echo "🎉 Сборка проекта завершена успешно!"
echo "📋 Для запуска приложения выполните:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo "   или"
echo "   gunicorn app:app" 
#!/bin/bash

# Скрипт для деплоя приложения на различные платформы

# Переменные
PLATFORM=$1

# Проверяем аргументы
if [ -z "$PLATFORM" ]; then
    echo "Ошибка: не указана платформа для деплоя"
    echo "Использование: ./deploy_platform.sh <platform>"
    echo "Доступные платформы: heroku, vercel, netlify, railway, render"
    exit 1
fi

# Функция для сборки приложения
build_app() {
    echo "🔨 Запуск скрипта сборки..."
    ./deploy.sh
}

# Деплой на Heroku
deploy_to_heroku() {
    echo "🚀 Деплой на Heroku..."
    
    # Проверяем, установлен ли Heroku CLI
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI не установлен. Установите его с помощью: brew install heroku/brew/heroku"
        exit 1
    fi
    
    # Проверяем, залогинен ли пользователь
    heroku whoami 2>/dev/null || { 
        echo "⚠️ Вы не вошли в аккаунт Heroku. Запускаем heroku login..."
        heroku login 
    }
    
    # Проверяем существование приложения
    HEROKU_APP_NAME="budgetnik-app"
    
    if ! heroku apps:info $HEROKU_APP_NAME &> /dev/null; then
        echo "📱 Создаем новое приложение Heroku: $HEROKU_APP_NAME"
        heroku apps:create $HEROKU_APP_NAME
    fi
    
    # Настраиваем приложение
    echo "⚙️ Настраиваем приложение Heroku..."
    heroku buildpacks:clear -a $HEROKU_APP_NAME
    heroku buildpacks:add heroku/python -a $HEROKU_APP_NAME
    heroku buildpacks:add heroku/nodejs -a $HEROKU_APP_NAME
    
    # Устанавливаем переменные окружения
    heroku config:set SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))') -a $HEROKU_APP_NAME
    heroku config:set DEBUG=False -a $HEROKU_APP_NAME
    
    # Деплой
    echo "🚀 Выполняем деплой..."
    git push heroku main
    
    echo "✅ Деплой на Heroku завершен!"
    echo "🌐 Приложение доступно по адресу: https://$HEROKU_APP_NAME.herokuapp.com"
}

# Деплой на Vercel
deploy_to_vercel() {
    echo "🚀 Деплой на Vercel..."
    
    # Проверяем, установлен ли Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI не установлен. Установите его с помощью: npm install -g vercel"
        exit 1
    }
    
    # Запускаем деплой
    echo "🚀 Выполняем деплой..."
    vercel --prod
    
    echo "✅ Деплой на Vercel завершен!"
}

# Деплой на Netlify
deploy_to_netlify() {
    echo "🚀 Деплой на Netlify..."
    
    # Проверяем, установлен ли Netlify CLI
    if ! command -v netlify &> /dev/null; then
        echo "❌ Netlify CLI не установлен. Установите его с помощью: npm install -g netlify-cli"
        exit 1
    }
    
    # Запускаем деплой
    echo "🚀 Выполняем деплой..."
    netlify deploy --prod
    
    echo "✅ Деплой на Netlify завершен!"
}

# Деплой на Railway
deploy_to_railway() {
    echo "🚀 Деплой на Railway..."
    
    # Проверяем, установлен ли Railway CLI
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI не установлен. Установите его с помощью: npm install -g @railway/cli"
        exit 1
    }
    
    # Запускаем деплой
    echo "🚀 Выполняем деплой..."
    railway up
    
    echo "✅ Деплой на Railway завершен!"
}

# Деплой на Render
deploy_to_render() {
    echo "🚀 Деплой на Render..."
    
    echo "⚠️ Для Render необходимо настроить деплой через веб-интерфейс."
    echo "1. Перейдите на https://dashboard.render.com/"
    echo "2. Создайте новый 'Web Service' и укажите URL вашего Git-репозитория"
    echo "3. Настройте следующие параметры:"
    echo "   - Build Command: ./deploy.sh"
    echo "   - Start Command: gunicorn app:app"
    echo "   - Добавьте переменные окружения (SECRET_KEY, DEBUG=False и т.д.)"
    
    echo "✅ Инструкции для деплоя на Render предоставлены!"
}

# Запускаем сборку приложения
build_app

# Выбираем платформу для деплоя
case $PLATFORM in
    heroku)
        deploy_to_heroku
        ;;
    vercel)
        deploy_to_vercel
        ;;
    netlify)
        deploy_to_netlify
        ;;
    railway)
        deploy_to_railway
        ;;
    render)
        deploy_to_render
        ;;
    *)
        echo "❌ Неизвестная платформа: $PLATFORM"
        echo "Доступные платформы: heroku, vercel, netlify, railway, render"
        exit 1
        ;;
esac 
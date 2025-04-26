#!/bin/bash

# Скрипт для сборки проекта на Netlify

echo "====== Начало сборки Budgetnik для Netlify ======"

# Установка зависимостей для функций Netlify
echo "Установка зависимостей для функций..."
mkdir -p netlify/functions/node_modules
cd netlify/functions
npm install --no-package-lock
cd ../..

# Создаем пакет для функций в корне проекта 
echo "Создание package.json в корне проекта для правильной установки зависимостей функций..."
cat > package.json << EOF
{
  "name": "budgetnik-project",
  "version": "1.0.0",
  "description": "Budgetnik - приложение для управления финансами",
  "engines": {
    "node": ">=18.0.0"
  },
  "dependencies": {
    "axios": "^1.6.2"
  }
}
EOF

# Устанавливаем зависимости в корневом пакете тоже
npm install --no-package-lock

# Подготовка и сборка фронтенда
echo "Сборка фронтенда..."
cd frontend
npm install
npm run build
cd ..

# Копирование _redirects, если его нет в сборке
echo "Проверка _redirects..."
if [ ! -f "frontend/dist/_redirects" ]; then
  echo "Копирование _redirects в директорию сборки..."
  cp frontend/public/_redirects frontend/dist/
fi

echo "====== Сборка завершена ======" 
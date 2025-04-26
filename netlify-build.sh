#!/bin/bash

# Скрипт для сборки проекта на Netlify

echo "====== Начало сборки Budgetnik для Netlify ======"

# Установка зависимостей для функций Netlify
echo "Установка зависимостей для функций..."
cd netlify/functions
npm install
cd ../..

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
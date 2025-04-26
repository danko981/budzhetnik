FROM node:16 AS frontend-builder

# Установка и сборка фронтенда
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.10-slim

# Установка зависимостей и настройка окружения
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Копирование собранного фронтенда из предыдущего этапа
COPY --from=frontend-builder /app/frontend/dist/ /app/static/

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD gunicorn --bind 0.0.0.0:$PORT app:app 
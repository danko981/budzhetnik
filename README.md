# Budgetnik

Приложение для управления личными финансами и бюджетом.

## Особенности

- 💰 Отслеживание доходов и расходов
- 📊 Визуальные отчеты и аналитика
- 💼 Управление бюджетами
- 🔄 Управление категориями
- 🧮 Финансовый калькулятор
- 📱 Адаптивный дизайн (мобильные устройства и десктоп)

## Упрощенная версия API

Если вы столкнулись с проблемами тайм-аутов при использовании основного API, в проекте доступна упрощенная версия системы аутентификации.

### Запуск упрощенной версии
```bash
# Запуск упрощенного API
chmod +x run_simple.sh
./run_simple.sh
```

Подробная информация о упрощенной версии API доступна в [README_SIMPLE_API.md](README_SIMPLE_API.md).

## Требования

- Python 3.8+
- Node.js 14+
- npm или yarn

## Установка и запуск

### Быстрый старт с помощью скрипта разработки
```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/budgetnik.git
cd budgetnik

# Запустите скрипт разработки
chmod +x run_dev.sh
./run_dev.sh
```

### Ручная установка

1. Создайте и активируйте виртуальное окружение Python:
```bash
python -m venv venv
source venv/bin/activate  # На Linux/macOS
# или
venv\Scripts\activate  # На Windows
```

2. Установите зависимости Python:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории:
```
DEBUG=True
FLASK_CONFIG=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///budgetnik.db
PORT=8000
```

4. Инициализируйте базу данных:
```bash
python init_db.py
```

5. Запустите бэкенд:
```bash
python wsgi.py
```

6. В отдельном терминале перейдите в директорию frontend и запустите фронтенд:
```bash
cd frontend
npm install
npm run dev
```

## Доступные сервисы

- Бэкенд: http://localhost:8000
- API Документация: http://localhost:8000/api/docs
- Фронтенд: http://localhost:5173

## API-эндпоинты

- `/api/status` - статус API
- `/api/v1/auth/*` - авторизация и пользователи
- `/api/v1/categories/*` - управление категориями
- `/api/v1/transactions/*` - управление транзакциями
- `/api/v1/budgets/*` - управление бюджетами
- `/api/v1/reports/*` - отчеты и аналитика
- `/api/v1/calculator/*` - финансовые калькуляторы

## Запуск с Docker

1. Сборка и запуск с Docker Compose:
```bash
docker-compose up -d
```

2. Откройте приложение в браузере: http://localhost:8000

## Структура проекта

```
budgetnik/
├── frontend/           # React фронтенд
│   ├── src/            # Исходный код
│   ├── public/         # Статические файлы
│   └── package.json    # Зависимости
├── views/              # API маршруты на flask_restx
├── app.py              # Основной файл Flask приложения
├── wsgi.py             # WSGI точка входа
├── models.py           # Модели данных
├── schemas.py          # Схемы валидации данных
├── config.py           # Конфигурация приложения
├── __init__.py         # Инициализация компонентов
├── services/           # Бизнес-логика
├── utils/              # Вспомогательные функции
├── tests/              # Тесты
├── init_db.py          # Инициализация базы данных
├── requirements.txt    # Python зависимости
├── run_dev.sh          # Скрипт для разработки
├── Dockerfile          # Dockerfile для контейнеризации
└── docker-compose.yml  # Конфигурация Docker Compose
```

## Развертывание

### Netlify / Vercel
```bash
# Настройте переменные окружения
FLASK_CONFIG=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-db-url
```

### Heroku
```bash
heroku create
git push heroku main
```

### Запуск на VPS
```bash
# На вашем сервере
git clone https://github.com/yourusername/budgetnik.git
cd budgetnik
pip install gunicorn
pip install -r requirements.txt
gunicorn wsgi:app
```

## Демо-данные

После инициализации базы данных вы можете войти с помощью следующих учетных данных:
- Логин: `demo`
- Пароль: `demo123`

## Технологии
- Бэкенд: Flask, SQLAlchemy
- Фронтенд: React, Vite

## Запуск приложения

### Предварительные требования
- Python 3.8+
- Node.js 14+
- npm или yarn

### Установка и запуск (без Docker)

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/budgetnik.git
cd budgetnik
```

2. Запустите скрипт сборки:
```bash
chmod +x deploy.sh
./deploy.sh
```

3. Запустите приложение:
```bash
source venv/bin/activate
python app.py
```

4. Откройте приложение в браузере: http://localhost:5000

### Установка и запуск с Docker

1. Сборка и запуск с Docker Compose:
```bash
docker-compose up -d
```

2. Откройте приложение в браузере: http://localhost:5000

## Деплой

### Heroku
```bash
heroku create
git push heroku main
```

### VPS (с Docker)
```bash
# На вашем сервере
git clone https://github.com/yourusername/budgetnik.git
cd budgetnik
docker-compose up -d
```

## Лицензия

[MIT](LICENSE)

## Автор

Ваше имя - [yourusername](https://github.com/yourusername) 
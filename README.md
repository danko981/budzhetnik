# Budgetnik - Приложение для управления личным бюджетом

Budgetnik - это веб-приложение для управления личными финансами, которое помогает отслеживать доходы, расходы, контролировать бюджет и анализировать финансовые данные.

## Особенности

- 💰 Отслеживание доходов и расходов
- 📊 Визуальные отчеты и аналитика
- 💼 Управление бюджетами
- 🔄 Управление категориями
- 🧮 Финансовый калькулятор
- 📱 Адаптивный дизайн (мобильные устройства и десктоп)

## Технологии

### Фронтенд
- React.js
- Material-UI
- React Router
- Chart.js

### Бэкенд
- Flask (Python)
- SQLAlchemy
- JWT для аутентификации

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

## Структура проекта

```
budgetnik/
├── frontend/           # React фронтенд
│   ├── src/            # Исходный код
│   │   ├── components/ # React компоненты
│   │   ├── pages/      # Страницы приложения
│   │   ├── services/   # API сервисы
│   │   └── context/    # React контексты
│   ├── public/         # Статические файлы
│   └── package.json    # Зависимости
├── app.py              # Основной файл Flask приложения
├── routes/             # API маршруты
├── models.py           # Модели данных
├── services/           # Бизнес-логика
├── utils/              # Вспомогательные функции
├── tests/              # Тесты
├── requirements.txt    # Python зависимости
├── deploy.sh           # Скрипт сборки и деплоя
├── Dockerfile          # Dockerfile для контейнеризации
└── docker-compose.yml  # Конфигурация Docker Compose
```

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